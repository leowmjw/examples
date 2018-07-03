# Copyright 2016-2018, Pulumi Corporation.  All rights reserved.

from importlib import import_module
import pulumi
from pulumi_aws import config, iam, sfn
_lambda = import_module('pulumi_aws.lambda')

lambda_role = iam.Role('lambdaRole',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

lambda_role_policy = iam.RolePolicy('lambdaRolePolicy',
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    }"""
)

sfn_role = iam.Role('sfnRole',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.%s.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }""" % config.region
)

sfn_role_policy = iam.RolePolicy('sfnRolePolicy',
    role=sfn_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": "*"
            }
        ]
    }"""
)

hello_world_fn = _lambda.Function('helloWorldFunction',
    role=lambda_role.arn,
    runtime="python2.7",
    handler="hello_step.hello",
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./step_hello')
    })
)

state_defn = state_machine = sfn.StateMachine('stateMachine',
    role_arn=sfn_role.arn,
    definition="""{
        "Comment": "A Hello World example of the Amazon States Language using an AWS Lambda Function",
        "StartAt": "HelloWorld",
        "States": {
            "HelloWorld": {
                "Type": "Task",
                "Resource": "%s",
                "End": true
            }
        }
    }""" % hello_world_fn.arn
)

pulumi.output('state_machine_arn', state_machine.id)
