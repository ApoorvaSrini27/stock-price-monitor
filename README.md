# README #

This repository is to peridocally monitor stock prices on NSE index and create alarms when stock prices breach predefined thresholds.

### What is this repository for? ###

* The app leverages AWSAppConfig to track the list of equities whose prices need monitoring.
  An event bridge triggers a lambda function periodically which first fetches the equities to monitor from AppConfig and fetches the price. The prices are emitted to Cloudwatch on which we can set alarms.
* Version: 0.1


### How do I get set up? ###

* Summary of set up
  * Clone the repository
  * Run `sam build`
  * On your AWS account, create a new role with permissions for:
    1. Accessing event bridge
    2. IAM access to create new policies
    3. CloudFormation access
    4. S3 access
    5. SNS access
    6. Lambda access
  *  Run `aws sts assume-role --role-arn <new role arn> --role-session-name SAMDeploySession`
  *  Set `AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN` based on output of above command
  *  Run `sam deploy --guided`
* Dependencies. All dependencies are in requirements.txt file

### Who do I talk to? ###
* [Apoorva Srinivasan](https://www.linkedin.com/in/apoorva-srinivasan-7805b6168/)
