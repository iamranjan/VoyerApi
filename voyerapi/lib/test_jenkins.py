from .jenkins import getLastBuildNumber, getLatestJobInfo, startJob, getJobStdout, getJobCompletionContent, startJobWithParameters
import time


def test_getLatestJobInfo():
    job = 'job-example-project'
    response = getLatestJobInfo(job)
    # print(response.json())
    assert response.status_code == 200



def test_getLastBuildNumber():
    job = 'job-example-project'
    build = getLastBuildNumber(job)
    print (build)
    assert isinstance(build, dict)


# def test_startJob():
#     job = 'job-example-project'
#     response = startJob(job)
#     print(response.text)
#     time.sleep(2)
#     assert response.status_code == 201

def test_startJobWithParameters():
    job = 'job-example-project'
    parameters = {
        "timer": "30",
        "tags": "full",
    }
    response = startJobWithParameters(job, parameters)
    print(response.text)
    time.sleep(2)
    assert response.status_code == 201


def test_getJobStdout():
        job = 'job-example-project'
        response = getJobStdout(job)
        print(response.text)
        assert response.status_code == 200


# def test_getJobCompletionContent():
#     job = 'job-example-project'
#     file = 'play1_output.json'
#     response = getJobCompletionContent(job, file)
#     assert response.status_code == 200



