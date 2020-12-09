#### TFW SDK for Python developers ####

This package is part of our next-gen Tutorial Framework (which just an additional abstraction layer). The purpose of the project is to decrease the learning curve of creating tutorial exercises, but it requires mandatory changes in the TFW baseimage as well.

#### Usage ####

In your solvable container you should prepare an `app.py` like this:

```python
from tfwsdk import sdk

def on_step(curent_state: int):
    sdk.message_send('CURRENT STATE: ' + str(curent_state))

def on_deploy(curent_state: int):
    sdk.message_send('DEPLOY BUTTON CLICKED')
    return True

def on_message_button_click(curent_state: int, button_value: str):
    sdk.message_send('MESSAGE BUTTON CLICKED: ' + button_value)

def on_ide_write(current_state: int, name_of_file: str, content_of_file: str):
    sdk.message_send('IDE WRITE')

def on_terminal_command(current_state: int, executed_command: str):
    sdk.message_send('COMMAND EXECUTED: ' + executed_command)

if __name__ == '__main__':
    print('🎉 SDK STARTED 🎉')
    sdk.start()
```

The SDK is running in the background (with supervisor), imports your `app.py` and executes the above functions on corresponding events. Also, it provides some really useful functions to communicate with the TFW. Naming convention is based on the `app.yml` file:

```
---
dashboard:
  stepToFirstStateAutomatically: true
  messageSpeed: 400 # Word per minute
  layout: web-only
  enabledLayouts:
    #- terminal-ide-web
    #- terminal-ide-vertical
    #- terminal-web
    #- ide-web-vertical
    - terminal-ide-horizontal
    #- terminal-only
    #- ide-only
    - web-only
webservice:
  iframeUrl: /webservice
  showUrlBar: false
  reloadIframeOnDeploy: false
terminal:
  directory: /home/user
  terminalMenuItem: terminal # terminal / console
ide:
  patterns: 
   - /home/user/tutorial/*
  showDeployButton: true
  deployButtonText:
    TODEPLOY:  Deploy
    DEPLOYED:  Deployed
    DEPLOYING: Reloading app...
    FAILED:    Deployment failed
```
