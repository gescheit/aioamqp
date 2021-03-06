"""
    Tests the heartbeat methods
"""

import asyncio
import unittest
from unittest import mock

from aioamqp.protocol import CLOSED

from . import testcase
from . import testing


class HeartbeatTestCase(testcase.RabbitTestCase, unittest.TestCase):

    @testing.coroutine
    def test_heartbeat(self):
        with mock.patch.object(
                self.amqp, 'send_heartbeat', wraps=self.amqp.send_heartbeat
                ) as send_heartbeat:
            # reset both timers to 1) make them 'see' the new heartbeat value
            # 2) so that the mock is actually called back from the main loop
            self.amqp.server_heartbeat = 0.5
            self.amqp._heartbeat_timer_send_reset()
            self.amqp._heartbeat_timer_recv_reset()
            self.amqp._start_heartbeat_send()
            self.amqp._start_heartbeat_recv()
            # connection must be closed after two missed hearbeats
            yield from asyncio.sleep(1.1)
            send_heartbeat.assert_called_once_with()

            yield from asyncio.sleep(1.1)
            self.assertEqual(self.amqp.state, CLOSED)
