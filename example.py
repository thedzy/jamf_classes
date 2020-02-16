#!/usr/bin/env python3

# Get varying policy differences

import jamf
import credentials

def main():
    api_url = 'https://jamf.example.com'

    try:
        api_user = credentials.api_user
        api_pass = credentials.api_pass
    except:
        print("Could not load credentials from credentials.py")
        exit()

    print('\nClassic API')

    # Get instance of Jamf Classic API
    with jamf.JamfClassic(api_url, api_user, api_pass) as api:
        print('\nComputer Serial Numbers:')

        # Will call https://jamf.example.com/v1/computers
        computers = api.get_data('computers')
        if computers.success:
            for computer in computers.data['computers']:
                # Will call https://jamf.example.com/v1/computers
                computer_info = api.get_data('computers', 'id', computer['id'])
                if computer_info.success:
                    print('  {}'.format(computer_info.data['computer']['general']['serial_number']))
                else:
                    print('Error')
                    print(computers.url)
                    print(computers.data)

        else:
            print('Error')
            print(computers.url)
            print(computers.data)

    print('\nUniversal API')

    # Get instance of Jamf Classic API
    uapi = jamf.JamfUAPI(api_url, api_user, api_pass)

    print('\nScript Names:')

    # Will call https://jamf.example.com/v1/scripts?sort=name:asc
    scripts = uapi.get_data('v1', 'scripts', sort='name:asc')
    if scripts.success:
        for result in scripts.data['results']:
            print('  {}'.format(result['name']))
    else:
        print('Error')
        print(scripts.url)
        print(scripts.data)


if __name__ == '__main__':
    main()