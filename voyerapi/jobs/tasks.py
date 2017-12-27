from __future__ import absolute_import, unicode_literals

from celery import task
from .models import Job, JobMetadata
from lib import jenkins
from kafka import KafkaConsumer
import re
import time
import json
from celery.utils.log import get_task_logger
from django.conf import settings
from inventory.lib.inventory import process_inventory

# logger = get_task_logger('JOBS')
logger = get_task_logger(__name__)


@task()
def add(x, y):
    logger.info('Adding {0} + {1}'.format(x, y))
    return x + y


@task()
def manageJenkinsJob(uuid):
    iterations = 0
    obj = Job.objects.get(uuid=uuid)
    job = obj.job
    parameters = {'timer': '5',
                  'username': obj.username,
                  'tags': ','.join(map(lambda x: x.name, obj.tags.all()))}
    lastBuildNumber = jenkins.getLastBuildNumber(job)
    jenkins.startJobWithParameters(job, parameters)
    time.sleep(0.2)
    build = jenkins.getLastBuild(job)
    obj.jobNumber = lastBuildNumber + 1
    obj.save()
    if build['number'] != lastBuildNumber + 1:
        logger.info(
            'JOBS:WARNING:JOBNUMBER_INCONSISTENT:FOUND:{}:---EXPECTED:{}'.format(build['number'], lastBuildNumber + 1))
        logger.info('JOBS:FINISH:JOB:PARAMETERS:{}'.format(build['parameters']))

    job_number = lastBuildNumber + 1
    meta_obj = JobMetadata(job=obj)
    meta_obj.save()
    while True:
        obj = Job.objects.get(uuid=uuid)
        if obj.status == "FINISHED":
            # TODO: add fetching of job post-deploy files and add to database
            # TODO: change this to obj.username from default 'demo'
            # s3_output = jenkins.getJobCompletionContent(job, "{}/s3_credentials.json".format(obj.username))
            # inventory = jenkins.getJobCompletionContent(job, "{}/inventory.json".format(obj.username))
            s3_output = jenkins.getJobCompletionContent(job, "{}/s3_credentials.json".format('demo'))
            inventory = jenkins.getJobCompletionContent(job, "{}/inventory.json".format('demo'))
            try:
                logger.info('JOBS:FINISH:S3:{}'.format(s3_output.json()))
                meta_obj.s3 = s3_output.json()
            except Exception as e:
                logger.info('JOBS:FINISH:EXCEPTION_PROCESSING_S3_JSON:E:{}'.format(e))
                meta_obj.s3 = "ERROR_PROCESSING"
            try:
                # logger.info('JOBS:FINISH:INVENTORY:{}'.format(inventory.json()))
                clean_inventory = dict(filter(lambda x: 'mgmt.pants.net' in x[0], inventory.json().items()))
                meta_obj.inventory = clean_inventory

            except Exception as e:
                logger.info('JOBS:FINISH:EXCEPTION_PROCESSING_INVENTORY_JSON:E:{}'.format(e))
                meta_obj.inventory = "ERROR_PROCESSING"
            meta_obj.save()
            inventory_processed = process_inventory(uuid)
            if inventory_processed:
                logger.info('JOBS:FINISH:PROCESS:INVENTORY:SUCCESS')
            else:
                logger.info('JOBS:FINISH:PROCESS:INVENTORY:FAILURE')
            if job != 'network-example':
                kafkaPoller.delay(uuid)
            else:
                logger.info('JOBS:FINISH:NO_KAFKA_POLLER_REQUIRED')
            # if job == 'pipeline_demo':
            #     kafkaPoller.delay(uuid)
            return "FINISHED"
        if iterations > 700:
            return "TIMED_OUT"
        stdout = jenkins.getJobStdout(job, job_number)
        if job == 'job-example-project':
            status = getExamplePipelineStatus(stdout.text)
        elif job == 'pipeline_demo':
            status = getPipelineDemoStatus(stdout.text)
        elif job == 'network-example':
            status = getNetworkSDNExampleStatus(stdout.text)
        logger.info('JOBS:ITERATION:{}'.format(iterations))
        logger.info('JOBS:STATUS:{}'.format(status))
        logger.info('JOBS:JOB_NUMBER:{}'.format(job_number))
        if status:
            obj.status = status['status']
            obj.progress = status['progress']
            meta_obj.stdout = stdout.text
            meta_obj.save()
            obj.save()
        iterations += 1
        time.sleep(4)


@task()
def kafkaPoller(uuid):
    """
    Responsible for polling/consume messages from kafka and adding them to the MetaJob object
    :param uuid:
    :return:
    """
    # TODO: get host information from inventory metadata
    logger.info('KAFKAPOLLER:STARTING')
    job_obj = Job.objects.get(uuid=uuid)
    logger.info('KAFKAPOLLER:UUID:{}'.format(uuid))
    logger.info('KAFKAPOLLER:UUID:{}'.format(uuid))
    meta_obj = JobMetadata.objects.get(job=job_obj)
    inventory = meta_obj.inventory
    if settings.KAFKA_HOST_MODE == "DEV":
        # ASSUMES SHUTTLE IS BEING USED FOR RESOLUTION + SSH TUNNEL TO KAFKA on localhost
        consumer = KafkaConsumer('demo', bootstrap_servers='{}:{}'.format('localhost', '9091'))
    elif settings.KAFKA_HOST_MODE == "STATIC":
        # ASSUMES SHUTTLE IS BEING USED FOR RESOLUTION + CONNECTIVITY
        consumer = KafkaConsumer('demo', bootstrap_servers='{}:{}'.format('demo-sc-kafka-01.mgmt.pants.net', '9093'))
    else:
        hostname, inventory_kafka = list(filter(lambda x: "kafka-01" in x[0], inventory.items()))[0]
        consumer = KafkaConsumer('demo', bootstrap_servers='{}:{}'.format(hostname, '9093'))
    window = 10
    iterations = 0
    while True:
        job_obj = Job.objects.get(uuid=uuid)
        # current_messages = meta_obj.kafka

        results = consumer.poll()
        if results:
            # print(results)
            # print(list(results.values()))
            for partition in results.keys():
                messages = results[partition]
                for message in messages:
                    meta_obj = JobMetadata.objects.get(job=job_obj)
                    current_messages = meta_obj.kafka
                    # logger.info('KAFKAPOLLER:KAFKA:MESSAGE:{}...'.format(message.value[0:20]))
                    if not current_messages.get("messages"):
                        logger.info('KAFKAPOLLER:KAFKA:CURRENT_MESSAGES_EMPTY:INITIALISING')
                        current_messages["messages"] = []

                    new_message = {'message': message.value.decode("utf-8"),
                                   'size': message.serialized_value_size,
                                   'received': message.timestamp}
                    # logger.info('KAFKAPOLLER:KAFKA::NEW_MESSAGE:VALUE:{}...'.format(new_message['message'][0:20]))
                    # logger.info('KAFKAPOLLER:KAFKA::NEW_MESSAGE:SIZE:{}'.format(new_message['size']))
                    # logger.info('KAFKAPOLLER:KAFKA::NEW_MESSAGE:RECEIVED:{}'.format(new_message['received']))
                    if len(current_messages["messages"]) >= window:
                        current_messages["messages"].pop()
                        current_messages["messages"].insert(0, new_message)
                    else:
                        current_messages["messages"].append(new_message)
                    # logger.info('KAFKAPOLLER:KAFKA::MESSAGES:LENGTH:{}'.format(len(current_messages["messages"])))
                    meta_obj.kafka = current_messages
                    meta_obj.save()
                    time.sleep(1)
        iterations += 1
        if job_obj.status == "DELETED":
            return "DELETED"
        if iterations > 5000:
            return "LONG_RUN_FINISHED"
        time.sleep(1)


    return "FINISHED"
    #consumer = KafkaConsumer('demo', bootstrap_servers=kafka_host)
def start_consumer(topic, brokers):
    """

    :param topic:
    :param brokers:
    :return:
    """

@task()
def deleteJenkinsJob(uuid):
    iterations = 0
    obj = Job.objects.get(uuid=uuid)
    job = obj.job
    if obj.username != "demo":
        parameters = {'timer': '0',
                      'username': obj.username,
                      'tags': 'purge-all'}
    else:
        parameters = {'timer': '0',
                      'username': "skipper",
                      'tags': 'purge-all'}

    logger.info('JOBS:FINISH:JOB:PARAMETERS:{}'.format(parameters))
    lastBuildNumber = jenkins.getLastBuildNumber(job)
    jenkins.startJobWithParameters(job, parameters)
    time.sleep(0.2)
    build = jenkins.getLastBuild(job)
    obj.jobNumber = lastBuildNumber + 1
    obj.save()
    if build['number'] != lastBuildNumber + 1:
        logger.info(
            'JOBS:WARNING:JOBNUMBER_INCONSISTENT:FOUND:{}:---EXPECTED:{}'.format(build['number'], lastBuildNumber + 1))
        logger.info('JOBS:FINISH:JOB:PARAMETERS:{}'.format(build['parameters']))

    job_number = lastBuildNumber + 1
    while True:
        obj = Job.objects.get(uuid=uuid)
        if obj.status == "DELETED":
            # TODO: add fetching of job post-deploy files and add to database
            return "DELETED"
        if iterations > 30:
            return "TIMED_OUT"
        stdout = jenkins.getJobStdout(job, job_number)
        status = getExamplePipelineDeleteStatus(stdout.text)
        logger.info('JOBS:ITERATION:{}'.format(iterations))
        logger.info('JOBS:STATUS:{}'.format(status))
        logger.info('JOBS:JOB_NUMBER:{}'.format(job_number))
        if status:
            obj.status = status['status']
            obj.progress = status['progress']
            obj.save()
        iterations += 1
        time.sleep(4)


@task()
def getExamplePipelineDeleteStatus(stdout):
    """
    Determine the pipeline status from a regex scan of the stdout
    :param stdout:
    :return: status
    """
    patterns = [
        {
            "status": "DELETED",
            "progress": 100,
            "order": 100,
            "regex": "Finished: ([A-Z]+)$"
        }
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern['regex'], stdout, re.MULTILINE)
        print("getPipelineStatus:STDOUT:len:%d" % len(stdout))
        if match:
            matches.append(pattern)
        else:
            continue

    if matches:
        logger.info('JOBS:MATCHES:{}'.format(matches))
        return matches[-1]
    else:
        logger.info('JOBS:NO-MATCHES')
        return None


def getPipelineDemoStatus(stdout):
    """
    Determine the pipeline status from a regex scan of the stdout
    :param stdout:
    :return: status
    """
    patterns = [
        {
            "status": "INITIALISING:CLEAR_ENV",
            "progress": 2,
            "order": 1,
            "regex": "^.*__STATE\|INITIALISING__.*$"
        },
        {
            "status": "CONFIGURE:S3",
            "progress": 5,
            "order": 2,
            "regex": "^.*__STATE\|CONFIGURE\|S3__.*$"
        },
        {
            "status": "PROVSIONING:LOGSTASH",
            "progress": 15,
            "order": 3,
            "regex": "^.*__STATE\|PROVISION\|LOGSTASH__.*$"
        },
        {
            "status": "CONFIGURING:LOGSTASH",
            "progress": 20,
            "order": 4,
            "regex": "^.*__STATE\|CONFIGURE\|LOGSTASH__.*$"
        },
        {
            "status": "PROVSIONING:KAFKA",
            "progress": 31,
            "order": 5,
            "regex": "^.*__STATE\|PROVISION\|KAFKA__.*$"
        },
        {
            "status": "PROVISIONING:ES+KIBANA",
            "progress": 39,
            "order": 6,
            "regex": "^.*__STATE\|PROVISION\|ES\+KIBANA__.*$"
        },
        {
            "status": "CONFIGURING:KAFKA",
            "progress": 54,
            "order": 7,
            "regex": "^.*__STATE\|CONFIGURE\|KAFKA__.*$"
        },
        {
            "status": "CONFIGURE:ELASTICSEARCH",
            "progress": 65,
            "order": 8,
            "regex": "^.*__STATE\|CONFIGURE\|ES\+KIBANA__.*$"
        },
        {
            "status": "CONFIGURE:KIBANA",
            "progress": 90,
            "order": 9,
            "regex": "^.*Install\ Kibana.*$"
        },
        {
            "status": "FINISHED",
            "progress": 100,
            "order": 100,
            "regex": "(Finished: ([A-Z]+)$)|(PLAY\ RECAP)"
        }
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern['regex'], stdout, re.MULTILINE)
        print("getPipelineStatus:STDOUT:len:%d" % len(stdout))
        if match:
            matches.append(pattern)
        else:
            continue

    if matches:
        logger.info('JOBS:MATCHES:{}'.format(matches))
        return matches[-1]
    else:
        logger.info('JOBS:NO-MATCHES')
        return None


def getExamplePipelineStatus(stdout):
    """
    Determine the pipeline status from a regex scan of the stdout
    :param stdout:
    :return: status
    """
    patterns = [
        {
            "status": "PLAY1",
            "progress": 33,
            "order": 1,
            "regex": "^.*APP1.*$"
        },
        {
            "status": "PLAY2",
            "progress": 66,
            "order": 2,
            "regex": "^.*APP2.*$"
        },
        {
            "status": "PLAY3",
            "progress": 90,
            "order": 3,
            "regex": "^.*APP3.*$"
        },
        {
            "status": "FINISHED",
            "progress": 100,
            "order": 100,
            "regex": "Finished: ([A-Z]+)$"
        }
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern['regex'], stdout, re.MULTILINE)
        print("getPipelineStatus:STDOUT:len:%d" % len(stdout))
        if match:
            matches.append(pattern)
        else:
            continue

    if matches:
        logger.info('JOBS:MATCHES:{}'.format(matches))
        return matches[-1]
    else:
        logger.info('JOBS:NO-MATCHES')
        return None


def getNetworkSDNExampleStatus(stdout):
    """
    Determine the pipeline status from a regex scan of the stdout
    :param stdout:
    :return: status
    """
    patterns = [
        {
            "status": "PROVISONING:CHECKPOINT",
            "progress": 5,
            "order": 1,
            "regex": "^.*STATE\|PROVISION\|CHECKPOINT.*$"
        },
        {
            "status": "PROVISION:CHECKPOINT:COMPLETE",
            "progress": 20,
            "order": 2,
            "regex": "^.*STATE\|ADD_HOSTS\|CHECKPOINT.*$"
        },
        {
            "status": "CONFIGURE:CHECKPOINT",
            "progress": 30,
            "order": 3,
            "regex": "^.*STATE\|CONFIGURE\|CHECKPOINT.*$"
        },
        {
            "status": "CONFIGURE:CHECKPOINT:COMPLETE",
            "progress": 45,
            "order": 4,
            "regex": "^.*STATE\|PROVISION\|F5.*$"
        },
        {
            "status": "PROVISIONING:F5",
            "progress": 50,
            "order": 5,
            "regex": "^.*STATE\|PROVISION\|F5.*$"
        },
        {
            "status": "PROVISIONING:COMPLETE:F5",
            "progress": 57,
            "order": 6,
            "regex": "^.*STATE\|LICENSING\|F5.*$"
        },
        {
            "status": "CONFIGURE:F5:BASIC",
            "progress": 75,
            "order": 7,
            "regex": "^.*STATE\|CONFIGURING\|BASIC\|F5.*$"
        },
        {
            "status": "CONFIGURE:F5:ADVANCED",
            "progress": 85,
            "order": 8,
            "regex": "^.*STATE\|CONFIGURING\|ADVANCED\|F5.*$"
        },
        {
            "status": "FINISHED",
            "progress": 100,
            "order": 100,
            "regex": "Finished: ([A-Z]+)$"
        }
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern['regex'], stdout, re.MULTILINE)
        print("getPipelineStatus:STDOUT:len:%d" % len(stdout))
        if match:
            matches.append(pattern)
        else:
            continue

    if matches:
        logger.info('JOBS:MATCHES:{}'.format(matches))
        return matches[-1]
    else:
        logger.info('JOBS:NO-MATCHES')
        return None
