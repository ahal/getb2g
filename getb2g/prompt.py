import sys

from base import valid_resources

def prompt(question, valid_answers=None):
    valid_answers = valid_answers or ('y','n')
    while True:
        print "%s (%s)" % (question, ', '.join(valid_answers))
        ans = raw_input("$ ").lower()
        if ans == 'q':
            sys.exit(0)
        if valid_answers and ans not in valid_answers:
            print "'%s' is not a valid option" % ans
            continue
        return ans

def prompt_resources(resources=None):
    resources = set(resources) or set([])

    if not valid_resources['device'].intersection(resources):
        device = prompt("What target device are you building for?",
                        valid_resources['device'])
        resources.add(device)

    for resource in valid_resources['all'].difference(valid_resources['device']).difference(resources):
        prompt("Do you want '%s'?" % resource)

    return resources
