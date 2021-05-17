
def lambda_handler(event, context):
    message = 'Hello {} {}!'.format(event['obj_name'], 
                                    event['body'])  
    return { 
        'message' : message
    }  
    