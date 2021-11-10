import boto3
from botocore.config import Config


def do():
    my_config = Config(
        region_name="us-east-2", retries={"max_attempts": 1, "mode": "standard"}
    )

    print("hey")
    client_ec2 = boto3.client("ec2", config=my_config)
    client_ssm = boto3.client("ssm", config=my_config)
    client_asg = boto3.client("autoscaling", config=my_config)
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
        )
        print(create_asg_result)

    except Exception as err:
        print(err)
    finally:
        client_ec2.delete_launch_template(LaunchTemplateId=launch_template_id)
        client_asg.delete_auto_scaling_group(AutoScalingGroupName=asg_name)


if __name__ == "__main__":
    do()
