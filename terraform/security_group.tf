resource "aws_security_group" "app" {
  name   = "${local.prefix}-app"
  vpc_id = "${data.aws_subnet.app.vpc_id}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["24.107.190.98/32"]
  }
}
