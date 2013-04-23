import getpass
import sys

prompt_disabled = False

def prompt(question, valid_answers=None):
    if prompt_disabled:
        return

    if valid_answers is None:
        valid_answers = ('y','n')

    while True:
        print "%s%s" % (question, ' (%s)' % ', '.join(valid_answers) if valid_answers else '')
        ans = raw_input("$ ").lower()
        if ans == 'q':
            sys.exit(0)
        if valid_answers and ans not in valid_answers:
            print "'%s' is not a valid option" % ans
            continue
        return ans

#convenience methods

def prompt_resources(valid_resources, resources=None):
    if prompt_disabled:
        return resources

    resources = set(resources) or set([])

    if not valid_resources['cli'].intersection(resources):
        device = prompt("What target device are you building for?",
                        valid_resources['device'])
        resources.add(device)

    temp_resources = resources.copy()
    for resource in temp_resources:
        for group in valid_resources['all']:
            if group in valid_resources and resource in valid_resources[group]:
                if prompt("Would you like to prepare '%s'?" % group) == 'y':
                    resources.add(group)
    return resources

def prompt_user_pass(url, user=None, password=None):
    """
    Prompts the user to provide any missing authentication information
    """
    if prompt_disabled:
        return (user, password)

    if not user or not password:
        if prompt("Do you have a user name and password for '%s'?" % url) == 'y':
            user = raw_input("Username: ")
            password = getpass.getpass()
    return (user, password)
