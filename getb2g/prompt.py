import sys

from base import valid_resources

def prompt(question, valid_answers=None)
    valid_answers = valid_answers or ['y','n']
    while True:
        print question
        print "valid options: %s" % ','.join(valid_answers)
        ans = raw_input("$ ").lower()
        if valid_answers and ans not in valid_answers:
            print "'%s' is not a valid option" % ans
            continue
        if ans == 'q':
            sys.exit(0)
        return ans

def prompt_resources(resources=None, metadata=None):
    resources = set(resources) or set([])

    if not resources.intersection(valid_resources['device']):
        device = prompt("What target device are you building for?",
                        valid_resources['device'])

    for resource in resources.difference(valid_resources['devices'].difference(valid_resources['all']))
        prompt("Do you want '%s'?" % resource)
