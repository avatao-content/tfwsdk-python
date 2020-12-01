from .zmq_connector import ZMQConnector
from tornado.ioloop import IOLoop
import importlib.util
import json
import logging
import os

LOG = logging.getLogger(__name__)

class SDK:
    def __init__(self):
        self.connector = ZMQConnector()
        self.current_state = 0
        self.event_handlers = None
        
    def _start(self):
        try:
            EVENT_HANDLERS = os.getenv('TFW_EVENT_HANDLERS', None) # Path to app.py (which contains event handler functions)
            if not EVENT_HANDLERS:
                LOG.error('TFW_EVENT_HANDLERS environment variable is missing. Please specify the path of `app.py` (which contains event handler functions).')
                exit(1)
            print(f'Event handlers will be loaded from: {EVENT_HANDLERS}')
            
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
        key = 'frontend.dashboard'
        payload = {
            'key': 'frontend.dashboard',
            'showUrlBar': str(value)
        }
        self.connector.send_message(payload)

    def webservice_reloadIframe(self):
        payload = {
            'key': 'frontend.reloadIframe'
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
            'content': content
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

    ########## CUSTOM ##########

    def custom_zmq_message(self, payload: dict):
        self.connector.send_message(payload)

sdk = SDK()

if __name__ == '__main__':
    print('🎉 SDK STARTED 🎉')
    sdk._start()