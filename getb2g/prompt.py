import getpass
import sys

prompt_disabled = False

def prompt(question, valid_answers=None):
    if prompt_disabled:
        return False

    valid_answers = valid_answers or ('y','n')
    while True:
        print "%s (%s)" % (question, ', '.join(valid_answers))
        ans = raw_input("$ ").lower()
        if ans == 'q':
            sys.exit(0)
        if ans not in valid_answers:
            print "'%s' is not a valid option" % ans
            continue
        return ans

#convenience methods

def prompt_resources(valid_resources, resources=None):
    if prompt_disabled:
        return resources

    resources = set(resources) or set([])

    if not valid_resources['device'].intersection(resources):
        device = prompt("What target device are you building for?",
                        valid_resources['device'])
        resources.add(device)
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
