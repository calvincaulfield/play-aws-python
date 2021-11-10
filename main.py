import boto3
from botocore.config import Config


def do():
    my_config = Config(
        region_name="us-east-2", retries={"max_attempts": 1, "mode": "standard"}
    )

    client_ec2 = boto3.client("ec2", config=my_config)
    client_ssm = boto3.client("ssm", config=my_config)
    client_asg = boto3.client("autoscaling", config=my_config)
    client_ecs = boto3.client("ecs", config=my_config)
    ssm_param_name = (
        "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
    )
    try:
        response = client_ssm.get_parameter(
            Name=ssm_param_name,
        )
        val = response["Parameter"]["Value"]
        print(f"Image id value {val}")

        create_launch_template_result = client_ec2.create_launch_template(
            DryRun=False,
            LaunchTemplateName="myname",
            LaunchTemplateData={
                "ImageId": val,
                # "IamInstanceProfile": {"Arn": "string", "Name": "string"},
                # "BlockDeviceMappings": [
                #     {
                #         # "DeviceName": "string",
                #         # "VirtualName": "string",
                #         "Ebs": {
                #             "Encrypted": True ,
                #             "DeleteOnTermination": True ,
                #             # "Iops": 123,
                #             # "KmsKeyId": "string",
                #             # "SnapshotId": "string",
                #             "VolumeSize": 10,
                #             "VolumeType": "standard"
                #             | "io1"
                #             | "io2"
                #             | "gp2"
                #             | "sc1"
                #             | "st1"
                #             | "gp3",
                #             "Throughput": 123,
                #         },
                #     },
                # ],
                "InstanceType": "t3.micro",
                # "SecurityGroupIds": [
                #     "string",
                # ],
                "TagSpecifications": [
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "k-nam",
                            },
                        ],
                    },
                    {
                        "ResourceType": "volume",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": "k-nam",
                            },
                        ],
                    },
                ],
            },
        )

        print(create_launch_template_result)
        launch_template_id = create_launch_template_result["LaunchTemplate"][
            "LaunchTemplateId"
        ]

        asg_name = "my-asg"
        create_asg_result = client_asg.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                "LaunchTemplateId": launch_template_id,
                "Version": "$Latest",
            },
            MinSize=0,
            MaxSize=4,
            VPCZoneIdentifier="subnet-04bfbc853588b9a8f",
            NewInstancesProtectedFromScaleIn=True,
            Tags=[
                {
                    "ResourceId": asg_name,
                    "ResourceType": "auto-scaling-group",
                    "Key": "name",
                    "Value": "k-nam",
                    "PropagateAtLaunch": True,
                },
            ],
        )
        response = client_asg.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
               asg_name,
            ],
        )
        print(response)
        asg_arn = response["AutoScalingGroups"][0]["AutoScalingGroupARN"]

        cp_name = "my-capacity-provider"
        create_cp_result = client_ecs.create_capacity_provider(
            name=cp_name,
            autoScalingGroupProvider={
                "autoScalingGroupArn": asg_arn,
                "managedScaling": {
                    "status": "ENABLED",
                    "minimumScalingStepSize": 1,
                    "maximumScalingStepSize": 10,
                    "instanceWarmupPeriod": 120,
                },
                "managedTerminationProtection": "ENABLED",
            },
            tags=[
                {"key": "string", "value": "string"},
            ],
        )
        response = client_ecs.describe_capacity_providers(
            capacityProviders=[
               cp_name,
            ],
        )
        print(response)

        cluster_name = "my-cluster"
        create_cluster_result = client_ecs.create_cluster(
            clusterName=cluster_name,
            tags=[
                {"key": "name", "value": "k-nam"},
            ],
            settings=[
                {"name": "containerInsights", "value": "enabled"},
            ],
            capacityProviders=[
                cp_name,
            ],
            defaultCapacityProviderStrategy=[
                {"capacityProvider": cp_name, "weight": 1, "base": 1},
            ],
        )
        response = client_ecs.describe_clusters(
            clusters=[
               cluster_name,
            ],
        )
        print(response)

    except Exception as err:
        print(err)
    finally:
        client_ec2.delete_launch_template(LaunchTemplateId=launch_template_id)
        client_asg.delete_auto_scaling_group(AutoScalingGroupName=asg_name)
        client_ecs.delete_capacity_provider(capacityProvider=cp_name)
        client_ecs.delete_cluster(cluster=cluster_name)


if __name__ == "__main__":
    do()
