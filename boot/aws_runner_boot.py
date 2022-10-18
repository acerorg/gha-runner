import os
import boto3

def handler() -> dict:
    billing_id = os.environ.get('E_BILLING_ID', 'GITHUB')
    project_name = os.environ.get('E_PROJECT_NAME', 'GitHub')

    runner_name = os.environ.get('E_RUNNER_NAME', 'runner-001')
    runner_tags = os.environ.get('E_RUNNER_TAGS', 'general')
    runner_ip = os.environ.get('E_RUNNER_IP', '1.2.3.4')
    subnet_id = os.environ.get('E_SUBNET_ID', 'subnet-00000000000000000')

    instanct_type = os.environ.get('E_INSTANCE_TYPE', 'c5n.xlarge')
    disk_size = int(os.environ.get('E_DISK_SIZE', 10))
    user_data = os.environ.get('E_USER_DATA', 'echo "Please provide your user data to init the runner"\n')

    gh_action_token = os.environ.get('E_TOKEN', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    gh_action_dl_url = os.environ.get('E_URL', 'https://github.com/actions/runner/releases/download/v2.298.2/actions-runner-linux-x64-2.298.2.tar.gz')

    repo_name = os.environ.get('GITHUB_REPOSITORY', 'acerorg/acerorg')
    region = os.environ.get('AWS_REGION', 'ap-southeast-2')

    template_name = f'GitHub/Runner/{repo_name}'
    ec2_client = boto3.client('ec2', region_name=region)
    tags = [
        {'Key': 'BillingID', 'Value': billing_id},
        {'Key': 'ProjectName', 'Value': project_name},
        {'Key': 'EnvName', 'Value': f'GitHub Action Runner @ {repo_name}'},
        {'Key': 'RepoName', 'Value': repo_name},
        {'Key': 'GitHub', 'Value': 'ActionRunner'},
        {'Key': 'Name', 'Value': f'GitHub/Runner/{repo_name}/{runner_name}'},
        {'Key': 'RunnerTag', 'Value': runner_tags},
        {'Key': 'RunnerName', 'Value': runner_name}
    ]
    tag_spec = [
        {'ResourceType': 'instance', 'Tags': tags},
        {'ResourceType': 'volume', 'Tags': tags},
        {'ResourceType': 'network-interface', 'Tags': tags},
        {'ResourceType': 'spot-instances-request', 'Tags': tags},
    ]
    block_device_mappings = [{
        'DeviceName': '/dev/xvda',
        'Ebs': {
            'DeleteOnTermination': True,
            'VolumeSize': disk_size,
            'VolumeType': 'gp3',
            'Encrypted': True
        },
    },]

    ec2_client.modify_launch_template(LaunchTemplateName=template_name, DefaultVersion='$Latest')

    response = ec2_client.run_instances(
        LaunchTemplate={'LaunchTemplateName': template_name},
        MaxCount=1,
        MinCount=1,
        SubnetId=subnet_id,
        PrivateIpAddress=runner_ip,
        InstanceType=instanct_type,
        BlockDeviceMappings=block_device_mappings,
        TagSpecifications=tag_spec,
        UserData=f'''#!/bin/env bash
set -x

{user_data}

file_name="$(basename "{gh_action_dl_url}")"

rm -rf /actions-runner
mkdir -v /actions-runner
cd /actions-runner
curl -s -L -o "./$file_name" "{gh_action_dl_url}"
tar xzf "./$file_name"
chown -R ec2-user:ec2-user /actions-runner

k=",aws"
k+=",{runner_name}"
k+=",{runner_tags}"
k+=",$(hostname -I | awk '{{print $1}}')"

sudo -u ec2-user bash -c "./config.sh --unattended --url 'https://github.com/{repo_name}' --token {gh_action_token} --labels '${{k}}' --name '{runner_name}'"
./svc.sh install ec2-user
./svc.sh start
                ''',
    )

    ec2_instance_id = response['Instances'][0]['InstanceId']
    request_id = response['Instances'][0]['SpotInstanceRequestId']

    ec2_client.get_waiter('instance_running').wait(InstanceIds=[ec2_instance_id], WaiterConfig={'Delay': 2, 'MaxAttempts': 90})

    return {'ec2_id': ec2_instance_id, 'request_id': request_id}


if __name__ == '__main__':
    response = handler()
    print(f"{response['ec2_id']},{response['request_id']}")
