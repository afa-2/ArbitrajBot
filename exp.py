list = [1]
x = 5
publish_without_networks = True


if publish_without_networks == True \
        or (publish_without_networks == False and len(order['matching_networks'] > 0)):
    print('yes')