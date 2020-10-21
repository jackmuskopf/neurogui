resource "aws_ecs_cluster" "app" {
  name = "${local.prefix}"
}

resource "aws_ecs_service" "app" {
  name             = "${var.service_name}"
  cluster          = "${aws_ecs_cluster.app.id}"
  platform_version = "1.4.0"
  task_definition  = "${aws_ecs_task_definition.app.arn}"
  desired_count    = "${var.init_task_count}"
  launch_type      = "FARGATE"

  network_configuration {
    subnets          = "${var.subnets}"
    security_groups  = ["${aws_security_group.app.id}"]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = ["desired_count"]
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.service_name}"
  task_role_arn            = "${aws_iam_role.service.arn}"
  execution_role_arn       = "${aws_iam_role.execution.arn}"
  cpu                      = "${var.task_cpu}"
  memory                   = "${var.task_memory}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  container_definitions    = <<EOF
[
  {
    "name": "${var.service_name}",
    "image": "${var.image_uri}",
    "essential": true,
    "environment": [
        {
            "name": "ENVIRONMENT",
            "value": "${var.environment}"
        }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "secretOptions": null,
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.log_group.name}",
        "awslogs-region": "${local.region}",
        "awslogs-stream-prefix": "jobs"
      }
    }
  }
]
EOF
}


