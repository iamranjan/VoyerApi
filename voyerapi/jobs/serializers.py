from .models import Job, Tag, JobMetadata
from rest_framework import serializers


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = Tag
        fields = ('name',)


class JobSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(max_length=24)
    # tags = serializers.ListField(child=TagSerializer())
    tags = TagSerializer(many=True)
    # tags = serializers.StringRelatedField(many=True, read_only=True)
    # uuid = serializers.UUIDField()
    job = serializers.CharField(max_length=50)

    # tags = TagSerializer(many=True)

    class Meta:
        model = Job
        fields = ('job', 'tags')

    def create(self, validated_data):
        # print("ManageCardsSerializer:create:")
        # print(validated_data)
        # print("JOB:%s" % validated_data['job'])
        # print("TAGS:%s" % validated_data['tags'])
        tags_data = validated_data['tags']
        job = Job(username=validated_data['username'],
                  job=validated_data['job'],
                  uuid=validated_data['uuid'],
                  )
        job.save()
        for tag in tags_data:
            Tag.objects.create(job=job, **tag)
        return job


class JobStatusSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(many=True)
    job = serializers.CharField(max_length=50)

    class Meta:
        model = Job
        fields = ('username', 'job', 'jobNumber', 'uuid', 'status', 'progress')


class JobMetadataSerializer(serializers.ModelSerializer):
    job = serializers.CharField(max_length=50)

    class Meta:
        model = JobMetadata
        fields = ('job', 's3', 'stdout', 'inventory', 'kafka')
