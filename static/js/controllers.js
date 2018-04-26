/**
 * INSPINIA - Responsive Admin Theme
 *
 * Main controller.js file
 * Define controllers with data used in Inspinia theme
 *
 *
 * Functions (controllers)
 *  - MainCtrl
 *
 *
 */

/**
 * MainCtrl - controller
 * Contains several global data used in different view
 *
 */
function MainCtrl($http) {


}

function loginCtrl($scope, $state, $http, $location) {
    $scope.user = {};

    $scope.login = function () {

        var config = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        $http.post('/login', $scope.user, config).then(
            function (response) {
                $state.go("home",{},{reload:true});
            },
            function (response) {
                alert("Invalid username and/or password");
            }
        );

    };
}

function homeCtrl($scope, $http, $compile, $uibModal, DTOptionsBuilder, DTColumnBuilder, info) {
    $scope.report = info;

    $scope.tasks = {};
    $scope.dtInstance = {};
    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withOption('ajax', {
            url: '/nmapui/tasks',
            type: 'GET',
            data: function (data) {
                var len = data.order.length;
                var sort_by_arr = [];
                var sort_context = [];

                for (var index = 0; index < len; index++) {
                    var sort_by = data.columns[data.order[index].column].data;
                    var dir = data.order[index].dir === 'asc' ? 1 : -1;
                    sort_by_arr.push(sort_by);
                    sort_context.push(dir);
                }

                var request = {
                    skip: data.start,
                    limit: data.length,
                    sort_by: sort_by_arr.join(','),
                    sort_context: sort_context.join(','),
                    search: data.search.value,
                    search_regex: data.search.regex
                };


                return request;

            },
            dataSrc: 'data'
        })
        .withOption('createdRow', createdRow)
        .withOption('processing', true)
        .withOption('serverSide', true)
        .withDisplayLength(10)
        .withOption('order', [0, 'desc'])
        .withDOM('<"html5buttons"B>lTfgitp')
        .withButtons([
            {extend: 'copy'},
            {extend: 'csv'},
            {extend: 'excel', title: 'ExampleFile'},
            {extend: 'pdf', title: 'ExampleFile'},

            {
                extend: 'print',
                customize: function (win) {
                    $(win.document.body).addClass('white-bg');
                    $(win.document.body).css('font-size', '10px');

                    $(win.document.body).find('table')
                        .addClass('compact')
                        .css('font-size', 'inherit');
                }
            }
        ]);

    $scope.dtColumns = [
        DTColumnBuilder.newColumn('targets').withTitle('Targets').withClass('text-center'),
        DTColumnBuilder.newColumn('options').withTitle('Options').withClass('text-center'),
        DTColumnBuilder.newColumn('create_date').withTitle('Create Date').withClass('text-center'),
        DTColumnBuilder.newColumn('status').withTitle('Status').withClass('text-center'),
        DTColumnBuilder.newColumn('progress').withTitle('Progress').withClass('text-center'),
        DTColumnBuilder.newColumn(null).withTitle('Actions').notSortable().withClass('text-center').renderWith(actionsHtml)
    ];

    function createdRow(row, data, dataIndex) {
        // Recompiling so we can bind Angular directive to the DT
        $compile(angular.element(row).contents())($scope);
    }

    function actionsHtml(data, type, full, meta) {
        $scope.tasks[data.id] = data;
        if (data.status !== 'SUCCESS') {
            return '<button class="btn btn-warning disabled">' +
                '<i class="fa fa-edit"></i>' +
                '</button>';
        } else {
            return '<button class="btn btn-warning" tooltip-placement="top" uib-tooltip="View Details" ng-click="showTaskDetails(\'' + data.id + '\')">' +
                '<i class="fa fa-edit"></i>' +
                '</button>';
        }
    }

    $scope.showTaskDetails = function (task_id) {
        $uibModal.open({
            templateUrl: '/nmapui/views/task_details.html',
            controller: 'taskDetailsCtrl',
            size: 'lg',
            resolve: {
                report_id: function () {
                    return task_id;
                }
            }
        }).result.then(function (data) {
            // de lam sau
        }, function () {
            // ko delete thi thoi
        });
    };
}

function taskDetailsCtrl($scope, $http, $uibModalInstance, report_id) {

    $http.get('/nmapui/report/' + report_id).then(
        function (response) {
            $scope.report = response.data.data;
        },
        function (response) {
            $scope.report = '';
        });


    $scope.ok = function () {
        $uibModalInstance.close();
    };

}

function taskCtrl($scope, $http, $compile, $uibModal, DTOptionsBuilder, DTColumnBuilder, toaster) {
    $scope.showAddForm = 1;
    $scope.addData = {};

    $scope.addTask = function () {

        var config = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        $http.post('/nmapui/tasks', $scope.addData, config).then(
            function (response) {
                $scope.clearForm();
                toaster.pop({
                    type: 'success',
                    title: response.data.code,
                    body: response.data.message,
                    showCloseButton: true,
                    timeout: 1000
                });
                $scope.dtInstance.reloadData(null, false);
            },
            function (response) {
                toaster.pop({
                    type: 'error',
                    title: response.data.code,
                    body: response.data.message,
                    showCloseButton: true,
                    timeout: 1000
                });
            }
        );

    };

    $scope.clearForm = function () {
        $scope.addData = {};
    };

    $scope.tasks = {};
    $scope.dtInstance = {};
    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withOption('ajax', {
            url: '/nmapui/tasks',
            type: 'GET',
            data: function (data) {
                var len = data.order.length;
                var sort_by_arr = [];
                var sort_context = [];

                for (var index = 0; index < len; index++) {
                    var sort_by = data.columns[data.order[index].column].data;
                    var dir = data.order[index].dir === 'asc' ? 1 : -1;
                    sort_by_arr.push(sort_by);
                    sort_context.push(dir);
                }

                var request = {
                    skip: data.start,
                    limit: data.length,
                    sort_by: sort_by_arr.join(','),
                    sort_context: sort_context.join(','),
                    search: data.search.value,
                    search_regex: data.search.regex
                };


                return request;

            },
            dataSrc: 'data'
        })
        .withOption('createdRow', createdRow)
        .withOption('processing', true)
        .withOption('serverSide', true)
        .withDisplayLength(10)
        .withOption('order', [0, 'desc'])
        .withDOM('<"html5buttons"B>lTfgitp')
        .withButtons([
            {extend: 'copy'},
            {extend: 'csv'},
            {extend: 'excel', title: 'ExampleFile'},
            {extend: 'pdf', title: 'ExampleFile'},

            {
                extend: 'print',
                customize: function (win) {
                    $(win.document.body).addClass('white-bg');
                    $(win.document.body).css('font-size', '10px');

                    $(win.document.body).find('table')
                        .addClass('compact')
                        .css('font-size', 'inherit');
                }
            }
        ]);

    $scope.dtColumns = [
        DTColumnBuilder.newColumn('targets').withTitle('Targets').withClass('text-center'),
        DTColumnBuilder.newColumn('options').withTitle('Options').withClass('text-center'),
        DTColumnBuilder.newColumn('create_date').withTitle('Create Date').withClass('text-center'),
        DTColumnBuilder.newColumn('status').withTitle('Status').withClass('text-center'),
        DTColumnBuilder.newColumn('progress').withTitle('Progress').withClass('text-center'),
        DTColumnBuilder.newColumn(null).withTitle('Actions').notSortable().withClass('text-center').renderWith(actionsHtml)
    ];

    function createdRow(row, data, dataIndex) {
        // Recompiling so we can bind Angular directive to the DT
        $compile(angular.element(row).contents())($scope);
    }

    function actionsHtml(data, type, full, meta) {
        $scope.tasks[data.id] = data;
        if (data.status !== 'SUCCESS') {
            return '<button class="btn btn-warning disabled">' +
                '<i class="fa fa-edit"></i>' +
                '</button>&nbsp;' +
                '<button class="btn btn-danger" tooltip-placement="top" uib-tooltip="Remove Task" ng-click="removeTask(\'' + data.id + '\')">' +
                '<i class="fa fa-trash-o"></i>' +
                '</button>';
        } else {
            return '<button class="btn btn-warning" tooltip-placement="top" uib-tooltip="View Details" ng-click="showTaskDetails(\'' + data.id + '\')">' +
                '<i class="fa fa-edit"></i>' +
                '</button>&nbsp;' +
                '<button class="btn btn-danger" tooltip-placement="top" uib-tooltip="Remove Task" ng-click="removeTask(\'' + data.id + '\')">' +
                '<i class="fa fa-trash-o"></i>' +
                '</button>';
        }
    }

    $scope.showTaskDetails = function (task_id) {
        $uibModal.open({
            templateUrl: '/nmapui/views/task_details.html',
            controller: 'taskDetailsCtrl',
            size: 'lg',
            resolve: {
                report_id: function () {
                    return task_id;
                }
            }
        }).result.then(function (data) {
            // de lam sau
        }, function () {
            // ko delete thi thoi
        });
    };

    $scope.removeTask = function (task_id) {

        toaster.pop({
            type: 'warning',
            title: '200',
            body: 'Waiting ....',
            showCloseButton: true,
            timeout: 3000
        });

        var config = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        $http.delete('/nmapui/tasks/' + task_id, config).then(
            function (response) {
                toaster.pop({
                    type: 'success',
                    title: response.data.code,
                    body: response.data.message,
                    showCloseButton: true,
                    timeout: 1000
                });
                $scope.dtInstance.reloadData(null, false);
            },
            function (response) {
                toaster.pop({
                    type: 'error',
                    title: response.data.code,
                    body: response.data.message,
                    showCloseButton: true,
                    timeout: 1000
                });
            }
        );
    };
}

/**
 *
 * Pass all functions into module
 */
angular
    .module('inspinia')
    .controller('MainCtrl', MainCtrl)
    .controller('loginCtrl', loginCtrl)
    .controller('homeCtrl', homeCtrl)
    .controller('taskDetailsCtrl', taskDetailsCtrl)
    .controller('taskCtrl', taskCtrl);

