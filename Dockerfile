# Copyright 2017 Yahoo Holdings. Licensed under the terms of the Apache 2.0 license. See LICENSE in the project root.
FROM centos:7
USER root

RUN yum-config-manager --add-repo https://copr.fedorainfracloud.org/coprs/g/vespa/vespa/repo/epel-7/group_vespa-vespa-epel-7.repo && \
    yum -y install epel-release && \
    yum -y install centos-release-scl && \
    yum -y install git bind-utils net-tools && \
	yum clean all

RUN yum install -y vespa && \
	yum clean all

EXPOSE 8080
EXPOSE 19092

COPY matscholar-vespa /matscholar-vespa

ADD start-container.sh /usr/local/bin/start-container.sh
RUN chmod +x /usr/local/bin/start-container.sh

ENTRYPOINT ["/usr/local/bin/start-container.sh"]