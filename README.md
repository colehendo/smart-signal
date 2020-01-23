# SmartSignal

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 8.3.10.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build
Run `ng build --prod` to build the project.
Run `aws s3 sync --delete dist/smart-signal s3://smart-signal` to update the files in S3.
Run `ssh -i ./smart-signal-ec2.pem ec2-user@54.196.101.72` to SSH into the EC2 instance.
Run `sudo su` to take root permissions.
Run `cd /var/www/html` to go to the file folder.
Run `aws s3 sync --delete s3://smart-signal/ ./` to update the files in EC2.
Run `exit` then `logout` to return to terminal.

## File Organization

`components` is for all pages--things like the homepage, account page, anything you can visit through a url
`core` contains singleton services, universal components and other features where there’s only once instance per application
`shared` is where any shared components, pipes/filters and services should go along with components used across the site like a button or drop down
`modules` is for modules like payloads, interfaces, and enums

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
