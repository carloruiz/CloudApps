'use strict';

console.log('Loading function');

//  should connect with mysql from RDS

const AWS = require("aws-sdk");
const dynamodb = new AWS.DynamoDB();

const doc = require('dynamodb-doc');
const dynamo = new doc.DynamoDB();
const docClient = new AWS.DynamoDB.DocumentClient();



/**
 * Demonstrates a simple HTTP endpoint using API Gateway. You have full
 * access to the request and response payload, including headers and
 * status code.
 *
 * To scan a DynamoDB table, make a GET request with the TableName as a
 * query string parameter. To put, update, or delete an item, make a POST,
 * PUT, or DELETE request respectively, passing in the payload to the
 * DynamoDB API as a JSON body.
 */
exports.handler = (event, context, callback) => {
    // console.log('Received event:', JSON.stringify(event, null, 2));
    // console.log('dynamo:', docClient);
    
    
    const done = (err, res) => callback(null, {
        statusCode: err ? '400' : '200',
        body: err ? err.message : JSON.stringify(res),
        headers: {
            'Content-Type': 'application/json',
        },
    });
    console.log("event" + JSON.stringify(event));

    switch (event.requestContext.httpMethod) {
        // case 'DELETE':
        //     // dynamo.deleteItem(JSON.parse(event.body), done);
        //     break;
        case 'GET':
            // var params = {
            //   TableName: 'person',
            // //   IndexName: 'Index',
            //   KeyConditionExpression: 'id = :hkey',
            //   ExpressionAttributeValues: {
            //     ':hkey': '1',
            //   }
            // };
        
            // docClient.query(params, function(err, data){
            //     if(err){
            //         // callback(err, null);
            //         console.log(err);
            //     }else{
            //         console.log(data);
            //     }
            // });
            console.log("hi!!");

            dynamo.scan({ TableName: 'person' }, done);
            break;
        case 'POST':
            dynamo.putItem(JSON.parse(event.body), done);
            break;
        // case 'PUT':
        //     // dynamo.updateItem(JSON.parse(event.body), done);
        //     break;
        default:
            done(new Error(`Unsupported method "${event.httpMethod}"`));
    }
};
