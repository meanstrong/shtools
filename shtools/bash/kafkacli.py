# -*- coding:utf-8 -*-
from optparse import OptionParser

import kafka

from .abstract_cmd import AbstractCmd

__all__ = ["kafkacli"]

parser = OptionParser(usage="kafkacli [-C|-P|-L|-Q] -b brokers [options...]", add_help_option=False)
parser.add_option("-C", action="store_true", dest="consumer", default=False, help="Consume data")
parser.add_option("-P", action="store_true", dest="producer", default=False, help="Produce data")
parser.add_option("-L", action="store_true", dest="lister", default=False, help="List topic metadata")
parser.add_option(
    "-Q", action="store_true", dest="querier", default=False, help="Query record offset for a given timestamp"
)
parser.add_option(
    "--security-protocol",
    action="store",
    dest="security_protocol",
    default="",
    help="Protocol used to communicate with brokers. Valid values are: PLAINTEXT, SSL. Default: PLAINTEXT.",
)
parser.add_option(
    "--sasl-mechanism",
    action="store",
    dest="sasl_mechanism",
    default="",
    help="Authentication mechanism when security_protocol is configured for SASL_PLAINTEXT or SASL_SSL. Valid values are: PLAIN, GSSAPI, OAUTHBEARER.",
)
parser.add_option(
    "--sasl-plain-username",
    action="store",
    dest="sasl_plain_username",
    default="",
    help="Username for sasl PLAIN authentication. Required if sasl_mechanism is PLAIN.",
)
parser.add_option(
    "--sasl-plain-password",
    action="store",
    dest="sasl_plain_password",
    default="",
    help="Password for sasl PLAIN authentication. Required if sasl_mechanism is PLAIN.",
)
parser.add_option("-b", action="append", dest="broker", default=[], help="broker, example: localhost:9092")
parser.add_option("-t", action="append", dest="topic", default=[], help="topic")
parser.add_option("-o", action="append", dest="offset", default=[], help="offset, example: beginning|end|stored; 123(absolute offset); -20(relative offset from the end); s@1234567800(timestamp in ms to start at); e@1234567900(timestamp in ms to stop at)")
parser.add_option("-c", action="store", type="int", dest="count", default=0, help="Exit after COUNT messages")
parser.add_option("--consumer-timeout", action="store", type="int", dest="consumer_timeout", default=0, help="number of milliseconds to block during consume message. Default block forever.")


class Result(object):
    def __init__(self, result):
        self._result = result

    @property
    def result(self):
        return self._result


class kafkacli(AbstractCmd):
    __option_parser__ = parser

    def connect(self):
        pass

    def close(self):
        if getattr(self, "client") is None:
            return
        self.client.close()

    def run(self):
        self.client = None
        configs = {}
        if not self.options.broker:
            raise ValueError("option [-b broker] is REQUIRED.")
        configs["bootstrap_servers"] = self.options.broker
        if self.options.security_protocol:
            configs["security_protocol"] = self.options.security_protocol
        if self.options.sasl_mechanism:
            configs["sasl_mechanism"] = self.options.sasl_mechanism
        if self.options.sasl_plain_username:
            configs["sasl_plain_username"] = self.options.sasl_plain_username
        if self.options.sasl_plain_password:
            configs["sasl_plain_password"] = self.options.sasl_plain_password
        if self.options.lister:
            if not self.options.topic:
                self.client = kafka.KafkaAdminClient(**configs)
                result = self.client.list_topics()
                return Result(result)
            elif len(self.options.topic) == 1:
                self.client = kafka.KafkaConsumer(*self.options.topic, **configs)
                topic = self.options.topic[0]
                partitions = [kafka.TopicPartition(topic, partition) for partition in self.client.partitions_for_topic(topic)]
                end_offsets = self.client.end_offsets(partitions)
                return Result(end_offsets)
        elif self.options.querier:
            if not self.options.topic or len(self.options.topic) != 1:
                raise ValueError("option [-c topic] is REQUIRED in querier.")
            topic, partition, timestamp = self.options.topic[0].split(":")
            self.client = kafka.KafkaConsumer(topic, **configs)
            result = self.client.offsets_for_times({kafka.TopicPartition(topic, int(partition)): int(timestamp)})
            return Result(result)
        elif self.options.consumer:
            if not self.options.topic:
                raise ValueError("option [-c topic] is REQUIRED in consumer.")
            if self.options.consumer_timeout:
                configs["consumer_timeout_ms"] = self.options.consumer_timeout
            if self.options.offset:
                if self.options.offset[0] == "beginning":
                    configs["auto_offset_reset"] = "earliest"
                elif self.options.offset[0] == "end":
                    configs["auto_offset_reset"] = "latest"
            self.client = kafka.KafkaConsumer(*self.options.topic, **configs)
            # self.client.poll(100)
            # print(f"{self.client.assignment()}")
            if self.options.offset:
                if self.options.offset[0].startswith("s@"):
                    timestamp = int(self.options.offset[0][2:])
                    topic = self.options.topic[0]
                    partitions = [kafka.TopicPartition(topic, partition) for partition in self.client.partitions_for_topic(topic)]
                    print(f"{partitions}")
                    offset_for_times = self.client.offsets_for_times({partition: timestamp for partition in partitions})
                    for partition in partitions:
                        offset_and_timestamp = offset_for_times[partition]
                        if offset_and_timestamp is not None:
                            self.client.seek(partition, offset_and_timestamp.offset)
                        # else:
                        #     offset = self.client.position(partition)
                        #     self.client.seek(partition, offset)
            if self.options.count:
                result = []
                for _ in range(self.options.count):
                    result.append(next(self.client))
                return Result(result)
        elif self.options.producer:
            raise NotImplementedError("NotImplemented")
        else:
            raise ValueError("one mode by option [-C|-P|-L|_Q] is REQUIRED")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
