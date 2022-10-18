import os
import sys
import boto3

def handler(action: str) -> dict:
    availabe_actions = ['start', 'stop', 'terminate']
    if action not in availabe_actions:
        raise Exception(f'Invalid action: "{action}", it must be one of {availabe_actions}.')

    runner_name = os.environ.get('E_RUNNER_NAME', 'runner-001')
    runner_ip = os.environ.get('E_RUNNER_IP', '1.2.3.4')

    repo_name = os.environ.get('GITHUB_REPOSITORY', 'acerorg/acerorg')
    region = os.environ.get('AWS_REGION', 'ap-southeast-2')

    ec2_resource = boto3.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)

    filters = [
        {"Name": "instance-state-name", "Values": ["pending", 'running', 'shutting-down', 'stopping', 'stopped']},
        {"Name": "tag:EnvName", "Values": [f'GitHub Action Runner @ {repo_name}']},
        {"Name": "tag:RepoName", "Values": [repo_name]},
        {"Name": "tag:GitHub", "Values": ["ActionRunner"]},
        {'Name': 'tag:Name', 'Values': [f'GitHub/Runner/{repo_name}/{runner_name}']},
        {'Name': 'tag:RunnerName', 'Values': [runner_name]},
        {'Name': 'private-ip-address', 'Values': [runner_ip]},
    ]
    instances = ec2_resource.instances.filter(Filters=filters)
    for instance in instances:
        if action=='start':
            ec2_client.start_instances(InstanceIds=[instance.id])
            ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance.id], WaiterConfig={'Delay': 2, 'MaxAttempts': 90})
        if action=='stop':
            ec2_client.stop_instances(InstanceIds=[instance.id])
            ec2_client.get_waiter('instance_stopped').wait(InstanceIds=[instance.id], WaiterConfig={'Delay': 2, 'MaxAttempts': 90})
        if action=='terminate':
            ec2_client.cancel_spot_instance_requests(SpotInstanceRequestIds=[instance.spot_instance_request_id])
            ec2_client.terminate_instances(InstanceIds=[instance.id])
            ec2_client.get_waiter('instance_terminated').wait(InstanceIds=[instance.id], WaiterConfig={'Delay': 2, 'MaxAttempts': 90})

        return {'ec2_id': instance.id, 'request_id': instance.spot_instance_request_id}
    else:
        raise Exception(f'Instance with runner name "{runner_name}" not found.')


if __name__ == '__main__':
    action = sys.argv[1]  # start, stop, terminate
    response = handler(action)
    print(f"{response['ec2_id']},{response['request_id']}")
