/**
 * INSPINIA - Responsive Admin Theme
 *
 * Inspinia theme use AngularUI Router to manage routing and views
 * Each view are defined as state.
 * Initial there are written state for all view in theme.
 *
 */
function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider, IdleProvider, $httpProvider) {

    // Configure Idle settings
    IdleProvider.idle(5); // in seconds
    IdleProvider.timeout(120); // in seconds

    $httpProvider.defaults.xsrfCookieName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRF-TOKEN';

    $urlRouterProvider.otherwise("/nmapui");

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });

    $stateProvider

        .state('login', {
            url: "/login",
            templateUrl: "views/nmapui/login.html",
            controller: 'loginCtrl',
            data: { pageTitle: 'Login', specialClass: 'gray-bg' }
        })
        .state('home', {
            url: "/nmapui",
            templateUrl: "/nmapui/views/home.html",
            controller: 'homeCtrl',
            data: { pageTitle: 'Home' },
            resolve: {
                 info : function($http){
                     return $http.get('/nmapui/task_statistics').then(
                        function (response) {
                            return response.data;
                        },
                        function (response) {
                            //
                        });
                },
                loadPlugin: function ($ocLazyLoad) {
                    return $ocLazyLoad.load([
                        {
                            insertBefore: '#loadBefore',
                            name: 'toaster',
                            files: ['/static/js/plugins/toastr/toastr.min.js', '/static/css/plugins/toastr/toastr.min.css']
                        },
                        {
                            files: ['/static/css/plugins/iCheck/custom.css','/static/js/plugins/iCheck/icheck.min.js']
                        },
                        {
                            serie: true,
                            files: ['/static/js/plugins/dataTables/datatables.min.js','/static/css/plugins/dataTables/datatables.min.css']
                        },
                        {
                            serie: true,
                            name: 'datatables',
                            files: ['/static/js/plugins/dataTables/angular-datatables.min.js']
                        },
                        {
                            serie: true,
                            name: 'datatables.buttons',
                            files: ['/static/js/plugins/dataTables/angular-datatables.buttons.min.js']
                        }
                    ]);
                }
            }
        })
        .state('tasks', {
            url: "/nmapui/tasks",
            templateUrl: "/nmapui/views/tasks.html",
            controller: 'taskCtrl',
            data: { pageTitle: 'Tasks' },
            resolve: {
                loadPlugin: function ($ocLazyLoad) {
                    return $ocLazyLoad.load([
                        {
                            insertBefore: '#loadBefore',
                            name: 'toaster',
                            files: ['/static/js/plugins/toastr/toastr.min.js', '/static/css/plugins/toastr/toastr.min.css']
                        },
                        {
                            files: ['/static/css/plugins/iCheck/custom.css','/static/js/plugins/iCheck/icheck.min.js']
                        },
                        {
                            serie: true,
                            files: ['/static/js/plugins/dataTables/datatables.min.js','/static/css/plugins/dataTables/datatables.min.css']
                        },
                        {
                            serie: true,
                            name: 'datatables',
                            files: ['/static/js/plugins/dataTables/angular-datatables.min.js']
                        },
                        {
                            serie: true,
                            name: 'datatables.buttons',
                            files: ['/static/js/plugins/dataTables/angular-datatables.buttons.min.js']
                        }
                    ]);
                }
            }
        })

}
angular
    .module('inspinia')
    .config(config)
    .run(function($rootScope, $state, $location, AuthService) {
        $rootScope.$state = $state;

        $rootScope.$on('$stateChangeStart', function (event, toState, fromState) {
            if (toState.name === "login") {
                return;
            }

            AuthService.getUserStatus()
                .then(function () {
                    if (!AuthService.isLoggedIn()) {
                        $state.go("login",{},{reload:true});
                    }
                });
        });
    });
