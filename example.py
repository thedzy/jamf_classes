#!/usr/bin/env python3

# Get varying policy differences

import argparse
import base64
import pydoc
import random

import credentials
import jamf


def main():
    show_classic = options.classic
    show_uapi = options.uapi

    if not any((show_uapi, show_classic)):
        show_classic = True
        show_uapi = True

    try:
        api_url = credentials.api_url
        api_user = credentials.api_user
        api_pass = credentials.api_pass
    except AttributeError as err:
        print(f'It seems that {err}')
        exit()

    if show_classic:
        div('Classic API', width=120)

        # Get instance of Jamf Classic API
        # Using "with"
        with jamf.JamfClassic(api_url, api_user, api_pass) as api:
            if options.show_all:
                # See all methods
                last_letter = 'a'
                for attribute in dir(api):
                    item = getattr(api, attribute)
                    if last_letter != attribute[0]:
                        last_letter = attribute[0]
                        div(last_letter.upper())

                    if callable(item) and not attribute.startswith('_'):
                        print(f'{attribute}()')

            if options.show_help:
                pydoc.pager = print
                pydoc.help(api.scripts_find_scripts_by_id)
                pydoc.help(api.mobiledevicecommands_find_mobile_device_commands_by_command)

            script = '''
            #!/usr/bin/env bash
            
            [ $(( RANDOM % 2 )) == 0 ] && echo Yes || echo No
            
            exit 0
            '''
            script_number = 0
            payload = f'''
                <script>
                    <id>{script_number}</id>
                    <name>script{random.randint(0, 100000)}.sh</name>
                    <category>Computers</category>
                    <filename>script.sh</filename>
                    <info/>
                    <notes/>
                    <priority>Before</priority>
                    <parameters/>
                    <os_requirements/>
                    <script_contents_encoded>{encode_script(script)}</script_contents_encoded>
                </script>
            '''

            div('Create script')
            new_script = api.scripts_create_script_by_id(id=script_number, data=payload)
            if new_script.is_json:
                new_script_id = new_script.json['script']['id']
                print(f'New script is number: {new_script_id}')
            else:
                print(new_script.data)

            div('Scripts on the server')
            jamf_scripts = api.scripts_find_scripts()
            jamf_scripts = sorted(jamf_scripts.json['scripts'], key=lambda x: x['id'])
            for jamf_script in jamf_scripts:
                print(f'ID: {jamf_script["id"]:3d}  {jamf_script["name"]}')

            div('Retrieve contents')
            script_retrieval = api.scripts_find_scripts_by_id(id=new_script_id)
            print(script_retrieval.json['script']['script_contents'])

            div('Delete script')
            script_delete = api.scripts_delete_script_by_id(id=new_script_id)
            if script_delete.success:
                print(f'Removed {new_script_id}')
            else:
                print('Failed to delete')

    if show_uapi:
        div('Universal API', width=120)

        # Get instance of Jamf Classic API
        uapi = jamf.JamfUAPI(api_url, api_user, api_pass, hide_deprecated=False)

        methods = []

        if options.show_all:
            # See all methods
            last_letter = 'a'
            for attribute in dir(uapi):
                item = getattr(uapi, attribute)
                if last_letter != attribute[0]:
                    last_letter = attribute[0]
                    div(last_letter.upper())

                if callable(item) and not attribute.startswith('_'):
                    print(f'{attribute}()')
                    methods.append(f'{attribute}()')

        if options.show_help:
            pydoc.pager = print
            pydoc.help(uapi.scripts_create_v1_scripts)
            pydoc.help(uapi.mdm_get_v1_mdm_commands)

        div('Deprecated function')
        deprecated_feature = uapi.jamf_pro_notifications_preview_get_notifications_alerts()

        script = '''
                 #!/usr/bin/env bash

                 [ $(( RANDOM % 2 )) == 0 ] && echo Yes || echo No

                 exit 0
                 '''
        script_number = 0
        payload = {
            'name': f'Test script {random.randint(0, 100000)}',
            'info': 'Test creation script',
            'notes': 'Test script',
            'priority': 'AFTER',
            'categoryId': '1',
            'categoryName': 'Computers',
            'parameter4': '',
            'parameter5': '',
            'parameter6': '',
            'parameter7': '',
            'parameter8': '',
            'parameter9': '',
            'parameter10': '',
            'parameter11': '',
            'osRequirements': '10.10.x',
            'scriptContents': trim_script(script)
        }

        div('Create script')
        new_script = uapi.scripts_create_v1_scripts(data=payload)
        new_script_id = new_script.json['id']
        print(f'New script is number: {new_script_id}')

        div('Scripts on the server')
        # Will call https://jamf.example.com/v1/scripts?sort=name:asc&page-size=10
        # Passing as dict keys keys with hyphens
        jamf_scripts = uapi.scripts_get_v1_scripts(**{'sort': 'id:asc', 'page-size': 10})
        print(jamf_scripts.url)
        for jamf_script in jamf_scripts.json['results']:
            print(f'ID: {int(jamf_script["id"]):3d}  {jamf_script["name"]}')

        div('Retrieve contents')
        script_retrieval = uapi.scripts_get_v1_scripts_by_id(id=new_script_id)
        print(script_retrieval.json['scriptContents'])

        div('Delete script')
        script_delete = uapi.scripts_delete_v1_scripts_by_id(id=new_script_id, data='')
        if script_delete.success:
            print(f'Removed {new_script_id}')
        else:
            print(script_delete)
            print('Failed to update')

        del uapi


def encode_script(script: str) -> str:
    """
    Returns a base64 encoded script

    :param script: Script as a string.
    :return: Base64 encoded script
    """

    return base64.b64encode(trim_script(script).encode()).decode()


def trim_script(script: str) -> str:
    """
    Trims empty beginning lines and removes leading spaces based on the first non-empty line's indentation.

    :param script: Script as a string.
    :return: Script as a string.
    """
    # Decode bytes to string and split into lines
    lines = script.splitlines()

    # Remove empty lines from the beginning
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return ''

    # Find leading spaces in the first non-empty line
    leading_spaces = len(lines[0]) - len(lines[0].lstrip(' '))

    # Remove the leading spaces from all lines
    dedented_lines = [line[leading_spaces:] if len(line) >= leading_spaces else line for line in lines]

    # Join back into a single string
    script = '\n'.join(dedented_lines)
    return script


def div(title='', width=40):
    hr = f'- {title} {"-" * width}'
    print()
    print(hr[0:width])


if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='Jamf acalss exmaples')

    parser.add_argument('--classic', default=False,
                        action='store_true', dest='classic',
                        help='classic api example')

    parser.add_argument('--uapi', default=False,
                        action='store_true', dest='uapi',
                        help='universal api example')

    parser.add_argument('-M', '--show-methods', default=False,
                        action='store_true', dest='show_all',
                        help='show all methods in class')

    parser.add_argument('-H', '--show-help', default=False,
                        action='store_true', dest='show_help',
                        help='show a samples of help')

    options = parser.parse_args()
    main()
