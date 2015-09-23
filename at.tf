variable "aws_region" {
  default = "us-east-1"
  description = "the region to use"
}

variable "aws_access_key" { description = "the API access key" }
variable "aws_secret_key" { description = "the API secret key" }

variable "resources_owner" { description = "the owner of the created resources" }

variable "ec2_ami" {
  default {
    "us-east-1" = "ami-96a818fe"
    "us-west-2" = "ami-c7d092f7"
  }
  description = "the AMI to launch the EC2 instance with"
}

variable "deploy_id" { description = "a unique ID for the deployment" }
variable "remote_user" { description = "the name of the user to login to the system with for provisioning" }

variable "package_repository" { description = "Owner and repository name (fmt: (<owner>/<repository>)" }

variable "proton_rpm" { description = "the path to the Proton RPM file" }
variable "datawire_rpm" { description = "the path to the Datawire Common RPM file" }
variable "directory_rpm" { description = "the path to the Datawire Directory RPM file" }

variable "watson_rpm" { description = "the path to the Datawire Watson RPM file" }
variable "sherlock_rpm" { description = "the path to the Datawire Sherlock RPM file" }

provider "aws" {
  region = "${var.aws_region}"

  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}

resource "aws_key_pair" "baker_street" {
  key_name   = "baker_street-${var.deploy_id}"
  public_key = "${file("${path.module}/tmp/temporary_key.pub")}"
}

resource "aws_vpc" "baker_street" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = false
  enable_dns_support = true
  instance_tenancy = "default"
  tags {
    Environment = "test"
    Name = "baker_street"
    Owner = "${var.resources_owner}"
    Role = "baker_street"
  }
}

resource "aws_internet_gateway" "baker_street_igw" {
  tags {
    Environment = "test"
    Name = "baker_street"
    Owner = "${var.resources_owner}"
    Role = "baker_street"
  }
  vpc_id = "${aws_vpc.baker_street.id}"
}

resource "aws_subnet" "baker_street" {
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags {
    Environment = "test"
    Name = "baker_street"
    Owner = "${var.resources_owner}"
    Role = "baker_street"
  }
  vpc_id = "${aws_vpc.baker_street.id}"
}

resource "aws_route_table" "baker_street" {
  route  = {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.baker_street_igw.id}"
  }
  tags {
    Environment = "test"
    Name = "baker_street"
    Owner = "${var.resources_owner}"
    Role = "baker_street"
  }
  vpc_id = "${aws_vpc.baker_street.id}"
}

resource "aws_route_table_association" "baker_street" {
  route_table_id = "${aws_route_table.baker_street.id}"
  subnet_id = "${aws_subnet.baker_street.id}"
}

resource "aws_security_group" "baker_street" {
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 0
    protocol = "-1"
    to_port = 0
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 22
    protocol = "tcp"
    to_port = 22
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 5672
    protocol = "tcp"
    to_port = 5672
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 5001
    protocol = "tcp"
    to_port = 5002
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 9001
    protocol = "tcp"
    to_port = 9001
  }
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = -1
    protocol = "icmp"
    to_port = -1
  }
  name = "baker_street"
  tags {
    Environment = "test"
    Name = "baker_street"
    Owner = "${var.resources_owner}"
    Role = "baker_street"
  }
  vpc_id = "${aws_vpc.baker_street.id}"
}

resource "aws_instance" "directory" {
  ami = "${lookup(var.ec2_ami, var.aws_region)}"
  associate_public_ip_address = true
  depends_on = ["aws_internet_gateway.baker_street_igw", "aws_key_pair.baker_street"]
  instance_type = "t2.micro"
  key_name = "${aws_key_pair.baker_street.key_name}"
  monitoring = false
  subnet_id = "${aws_subnet.baker_street.id}"
  tags {
    Environment = "test"
    Name = "directory-test-${var.resources_owner}"
    Owner = "${var.resources_owner}"
    Role = "directory"
  }
  vpc_security_group_ids = [
    "${aws_security_group.baker_street.id}"
  ]

  connection {
    user = "${var.remote_user}"
    key_file = "${path.module}/tmp/temporary_key"
  }

  provisioner "file" {
    source = "${var.proton_rpm}"
    destination = "/home/centos/datawire-proton.rpm"
  }

  provisioner "file" {
    source = "${var.datawire_rpm}"
    destination = "/home/centos/datawire.rpm"
  }

  provisioner "file" {
    source = "${var.directory_rpm}"
    destination = "/home/centos/datawire-directory.rpm"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum -y install datawire-proton.rpm datawire.rpm datawire-directory.rpm",
      "printf '[Datawire]\ndirectory_host=${self.private_ip}' | sudo tee -a /etc/datawire/directory.conf",
      "sudo systemctl start directory.service"
    ]
  }
}

resource "template_file" "watson_config_nopath" {
    filename = "${path.module}/resources/infrastructure-setup/templates/watson-test_service-nopath.conf.tpl"
    vars {
      directory_host = "${aws_instance.directory.private_ip}"
    }
}

resource "template_file" "watson_config_path" {
    filename = "${path.module}/resources/infrastructure-setup/templates/watson-test_service-path.conf.tpl"
    vars {
      directory_host = "${aws_instance.directory.private_ip}"
    }
}

resource "template_file" "sherlock_config" {
    filename = "${path.module}/resources/infrastructure-setup/templates/sherlock.conf.tpl"
    vars {
      directory_host = "${aws_instance.directory.private_ip}"
    }
}

resource "aws_instance" "test_service" {
  ami = "${lookup(var.ec2_ami, var.aws_region)}"
  associate_public_ip_address = true
  depends_on = [
    "aws_internet_gateway.baker_street_igw",
    "aws_key_pair.baker_street",
    "aws_instance.directory"
  ]
  instance_type = "t2.micro"
  key_name = "${aws_key_pair.baker_street.key_name}"
  monitoring = false
  subnet_id = "${aws_subnet.baker_street.id}"
  tags {
    Environment = "test"
    Name = "test_service-test-${var.resources_owner}"
    Owner = "${var.resources_owner}"
    Role = "foobar_service"
  }
  vpc_security_group_ids = [
    "${aws_security_group.baker_street.id}"
  ]

  connection {
    user = "${var.remote_user}"
    key_file = "${path.module}/tmp/temporary_key"
  }

  provisioner "file" {
    source = "${var.proton_rpm}"
    destination = "/home/centos/datawire-proton.rpm"
  }

  provisioner "file" {
    source = "${var.datawire_rpm}"
    destination = "/home/centos/datawire.rpm"
  }

  provisioner "file" {
    source = "${var.watson_rpm}"
    destination = "/home/centos/datawire-watson.rpm"
  }

  provisioner "file" {
    source = "${path.module}/resources/infrastructure-setup/bin/test_service.py"
    destination = "/home/centos/test_service.py"
  }

  provisioner "file" {
    source = "${path.module}/resources/infrastructure-setup/bin/watson_controller.py"
    destination = "/home/centos/watson_controller.py"
  }

  provisioner "file" {
    source = "${path.module}/resources/infrastructure-setup/config/watson_controller.yml"
    destination = "/home/centos/watson_controller.yml"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm",
      "sudo yum -y install python-pip",
      "yes | sudo pip install flask",

      "sudo yum -y install datawire-proton.rpm datawire.rpm datawire-watson.rpm",

      "chmod +x /home/centos/test_service.py",
      "chmod +x /home/centos/watson_controller.py",

      "sudo cat > /tmp/watson-test_service-nopath.conf << EOF",
      "${template_file.watson_config_nopath.rendered}",
      "EOF",

      "printf '\nservice_url: http://${self.private_ip}:5001' | sudo tee -a /tmp/watson-test_service-nopath.conf",

      "sudo cat > /tmp/watson-test_service-path.conf << EOF",
      "${template_file.watson_config_path.rendered}",
      "EOF",

      "printf '\nservice_url: http://${self.private_ip}:5001/hello' | sudo tee -a /tmp/watson-test_service-path.conf",

      "sudo mv /tmp/watson-test_service-nopath.conf /etc/datawire/watson-test_service-nopath.conf",
      "sudo mv /tmp/watson-test_service-path.conf /etc/datawire/watson-test_service-path.conf",

      "nohup /home/centos/test_service.py &> test_service.out&",
      "nohup /home/centos/watson_controller.py -c /home/centos/watson_controller.yml &> watson_controller.out&",

      "sleep 5",
    ]
  }
}

resource "aws_instance" "test_runner" {
  ami = "${lookup(var.ec2_ami, var.aws_region)}"
  associate_public_ip_address = true
  depends_on = [
    "aws_internet_gateway.baker_street_igw",
    "aws_key_pair.baker_street",
    "aws_instance.directory"
  ]
  instance_type = "t2.micro"
  key_name = "${aws_key_pair.baker_street.key_name}"
  monitoring = false
  subnet_id = "${aws_subnet.baker_street.id}"
  tags {
    Environment = "test"
    Name = "test_runner-test-${var.resources_owner}"
    Owner = "${var.resources_owner}"
    Role = "foobar_service_tests"
  }
  vpc_security_group_ids = [
    "${aws_security_group.baker_street.id}"
  ]

  connection {
    user = "${var.remote_user}"
    key_file = "${path.module}/tmp/temporary_key"
  }

  provisioner "file" {
    source = "${var.proton_rpm}"
    destination = "/home/centos/datawire-proton.rpm"
  }

  provisioner "file" {
    source = "${var.datawire_rpm}"
    destination = "/home/centos/datawire.rpm"
  }

  provisioner "file" {
    source = "${var.sherlock_rpm}"
    destination = "/home/centos/datawire-sherlock.rpm"
  }

  provisioner "file" {
    source = "${path.module}/tests/conftest.py"
    destination = "/home/centos/conftest.py"
  }

  provisioner "file" {
    source = "${path.module}/tests/test_bakerstreet.py"
    destination = "/home/centos/test_bakerstreet.py"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm",
      "sudo yum -y install python-pip",
      "sudo yum -y install datawire-proton.rpm datawire.rpm datawire-sherlock.rpm",

      "yes | sudo pip install pytest flask",

      "sudo cat > /tmp/sherlock.conf << EOF",
      "${template_file.sherlock_config.rendered}",
      "EOF",
      "sudo mv /tmp/sherlock.conf /etc/datawire/sherlock.conf",

      "sudo systemctl start sherlock.service",

      "sleep 5"
    ]
  }
}

output "test_runner_public_ip" {
  value = "${aws_instance.test_runner.public_ip}"
}

output "test_service_private_ip" {
  value = "${aws_instance.test_service.private_ip}"
}