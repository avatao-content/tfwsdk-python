from .zmq_connector import ZMQConnector
from tornado.ioloop import IOLoop
import importlib.util
import json
import logging
import os
import sys

LOG = logging.getLogger(__name__)

class SDK:
    def __init__(self):
        self.connector = ZMQConnector()
        self.current_state = 0
        self.event_handlers = None
        
    def start(self):
        try:
            EVENT_HANDLERS = os.path.dirname(os.path.realpath(sys.argv[0])) + '/' + sys.argv[0] # Path to app.py (which contains event handler functions)
            print(f'Loading event handlers from: {EVENT_HANDLERS}')
            
            # Loading the app.py functions dynamically
            # I know it's a little bit magic, but this way we can keep the app.py as clean as possible
            spec = importlib.util.spec_from_file_location('event_handlers', EVENT_HANDLERS)
            self.event_handlers = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.event_handlers)
            # Now we should be able to access user-defined functions as `self.event_handlers.on_...`

            self.connector.register_callback(self.__on_message)
            IOLoop.current().start()
        except KeyboardInterrupt:
            self.connector.close()
            IOLoop.current().stop()
        except Exception as e:
            LOG.error(e)
            exit(2)

    # The main switch case - it routes the messages to the corresponding event handlers
    def __on_message(self, message):
        
        try:
            message = [x.decode('utf-8') for x in message]
            key, message = message[0], json.loads(message[1])
        except Exception as e:
            LOG.error(e)
            return

        if key == 'fsm.update':
            self.current_state = int(message['current_state'])
            try:
                self.event_handlers.on_step(self.current_state)
            except Exception as e:
                LOG.error('on_step: ' + str(e))

        if key == 'message.button.click':
            try:
                self.event_handlers.on_message_button_click(self.current_state, message['value'])
            except Exception as e:
                LOG.error('on_message_button_click: ' + str(e))

        if key == 'deploy.start':
            success = False
            try:
                success = self.event_handlers.on_deploy(self.current_state)
            except Exception as e:
                LOG.error('on_deploy: ' + str(e))

            tfw_message = {'key': 'deploy.finish'}
            if not success:
                tfw_message['error'] = True
            self.connector.send_message(tfw_message)

        if key == 'ide.write':
            try:
                self.event_handlers.on_ide_write(self.current_state, message['filename'], message['content'])
            except Exception as e:
                LOG.error('on_ide_write: ' + str(e))

        if key == 'history.bash':
            try:
                self.event_handlers.on_terminal_command(self.current_state, message['command'])
            except Exception as e:
                LOG.error('on_terminal_command: ' + str(e))

    ########## MESSAGING ##########

    def message_queue(self, messages: list):
        messages = [{'message': message, 'originator': 'avataobot'} for message in messages]
        payload = {
            'key': 'message.queue', 
            'messages': messages
        }
        self.connector.send_message(payload)

    def message_send(self, message: str):
        payload = {
            'key': 'message.send',
            'originator': 'avataobot',
            'message': message
        }
        self.connector.send_message(payload)

    ########## STATES ##########

    def step(self, state: int = 0, force: bool = False):
        '''
        By default it steps to the next state.

        If you provide a state parameter, then the framework steps to the provided state, if it's the next one (otherwise nothing happens). 
        You can step to it anyway by calling it with `force = True`.
        '''
        if not state:
            state = self.current_state +1
        if force:
            payload = {'key': 'fsm.trigger', 'transition': 'to_' + str(state)}
        else:
            payload = {'key': 'fsm.trigger', 'transition': 'step_' + str(state)}
        self.connector.send_message(payload)

    ########## DASHBOARD ##########

    def dashboard_layout(self, layout: str):
        payload = {
            'key': 'frontend.dashboard',
            'layout': layout
        }
        self.connector.send_message(payload)

    ########## WEBSERVICE ##########

    def webservice_iframeUrl(self, url: str):
        payload = {
            'key': 'frontend.dashboard',
            'iframeUrl': url
        }
        self.connector.send_message(payload)

    def webservice_showUrlBar(self, value: bool):
        payload = {
            'key': 'frontend.dashboard',
            'showUrlBar': str(value)
        }
        self.connector.send_message(payload)

    def webservice_reloadIframe(self):
        payload = {
            'key': 'dashboard.reloadIframe'
        }
        self.connector.send_message(payload)

    ########## TERMINAL / CONSOLE ##########

    def terminal_terminalMenuItem(self, item: str):
        payload = {
            'key': 'frontend.dashboard',
            'terminalMenuItem': item
        }
        self.connector.send_message(payload)

    def terminal_write(self, content: str):
        payload = {
            'key': 'terminal.write',
            'command': content
        }
        self.connector.send_message(payload)

    def console_write(self, content: str):
        payload = {
            'key': 'console.write',
            'content': content
        }
        self.connector.send_message(payload)

    ########## IDE ##########

    def ide_selectFile_and_patterns(self, filename: str, patterns: list = None):
        payload = {
            'key': 'ide.read',
            'filename': filename
        }

        if patterns:
            payload['patterns'] = patterns

        self.connector.send_message(payload)

    def ide_showDeployButton(self, value: bool):
        payload = {
            'key': 'frontend.ide',
            'showDeployButton': value
        }
        self.connector.send_message(payload)

    def ide_deployButtonText(self, values: list):
        if len(values) != 4:
            LOG.error('"ide_deployButtonText" expects a list with 4 items')
            return

        payload = {
            'key': 'frontend.ide',
            'deployButtonText': {
                'TODEPLOY':  values[0],
                'DEPLOYED':  values[1],
                'DEPLOYING': values[2],
                'FAILED':    values[3]
            }
        }
        self.connector.send_message(payload)

    ########## CUSTOM ##########

    def custom_zmq_message(self, payload: dict):
        self.connector.send_message(payload)

sdk = SDK()
