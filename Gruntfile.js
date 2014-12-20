/*global module:false*/
module.exports = function (grunt) {

    // Project configuration.
    grunt.initConfig({
        // Metadata.
        pkg: grunt.file.readJSON('package.json'),
        banner: '/*! <%= pkg.title || pkg.name %> - v<%= pkg.version %> - ' +
            '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
            '<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
            '* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;' +
            ' Licensed <%= _.pluck(pkg.licenses, "type").join(", ") %> */\n',
        // Task configuration.
        concat: {
            options: {
                banner: '<%= banner %>',
                stripBanners: true
            },
            app: {
                src: ['components/js/*.js'],
                dest: 'static/js/app.js'
            },
            libs: {
                src: [
                    'components/bower/angular/angular.js',
                    'components/bower/angular-route/angular-route.js',
                    'components/bower/angular-resource/angular-resource.js'
                ],
                dest: 'static/js/libs.js'
            }
        },
        uglify: {
            options: {
                banner: '<%= banner %>'
            },
            app: {
                src: '<%= concat.app.dest %>',
                dest: 'static/js/app.min.js'
            },
            libs: {
                src: '<%= concat.libs.dest %>',
                dest: 'static/js/libs.min.js'
            }
        },
        jshint: {
            options: {
                curly: true,
                eqeqeq: true,
                immed: true,
                latedef: true,
                newcap: true,
                noarg: true,
                sub: true,
                undef: true,
                unused: true,
                boss: true,
                eqnull: true,
                browser: true,
                globals: {}
            },
            gruntfile: {
                src: 'Gruntfile.js'
            },
            app: {
                options: {
                    unused: false,
                    globals: {
                        "angular": true
                    }
                },
                src: 'components/js/*.js'
            }
        },
        watch: {
            gruntfile: {
                files: '<%= jshint.gruntfile.src %>',
                tasks: ['jshint:gruntfile']
            },
            app_js: {
                files: 'components/js/*.js',
                tasks: ['jshint:app', 'concat:app', 'uglify:app']
            }
        }
    });

    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Default task.
    grunt.registerTask('default', ['jshint', 'concat:app', 'uglify:app']);
    grunt.registerTask('libs', ['concat:libs', 'uglify:libs']);

};
