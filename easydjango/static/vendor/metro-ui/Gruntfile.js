module.exports = function(grunt) {

    "use strict";

    require('load-grunt-tasks')(grunt);

    var autoprefixer = require('autoprefixer');

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        banner: '/*!\n' +
                ' * Metro UI CSS v<%= pkg.version %> (<%= pkg.homepage %>)\n' +
                ' * Copyright 2012-<%= grunt.template.today("yyyy") %> <%= pkg.author %>\n' +
                ' * Licensed under <%= pkg.license.type %> (<%= pkg.license.url %>)\n' +
                ' */\n',

        requirejs_banner: "\n(function( factory ) {\n"+
                          "    if ( typeof define === 'function' && define.amd ) {\n" +
                          "        define([ 'jquery' ], factory );\n"+
                          "    } else {\n" +
                          "        factory( jQuery );\n"+
                          "    }\n"+
                          "}(function( jQuery ) { \n'use strict';\n\nvar $ = jQuery;\n\n",

        clean: {
            build: ['build/js', 'build/css', 'build/fonts'],
            docs: ['docs/css/metro*.css', 'docs/js/metro*.js'],
            compiled_html: ['.compiled_html']
        },

        concat: {
            options: {
                banner: '<%= banner %>' + '<%= requirejs_banner%>',
                footer: "\n\n return $.Metro.init();\n\n}));",
                stripBanners: true,
                process: function(src, filepath) {
                    return '// Source: ' + filepath + '\n' +
                        src.replace(/(^|\n)[ \t]*('use strict'|"use strict");?\s*/g, '$1');
                }
            },
            metro: {
                src: [
                    'js/requirements.js',
                    'js/global.js',
                    'js/widget.js',
                    'js/initiator.js',
                    'js/utils/*.js',
                    'js/widgets/*.js'
                ],
                dest: 'build/js/<%= pkg.originName %>.js'
            }
        },

        uglify: {
            options: {
                banner: '<%= banner %>',
                stripBanners: false,
                sourceMap: false
            },
            metro: {
                src: '<%= concat.metro.dest %>',
                dest: 'build/js/<%= pkg.originName %>.min.js'
            }
        },

        less: {
            options: {
                paths: ['less'],
                strictMath: false
            },
            compileCore: {
                src: 'less/<%= pkg.originName %>.less',
                dest: 'build/css/<%= pkg.originName %>.css'
            },
            compileResponsive: {
                src: 'less/<%= pkg.originName %>-responsive.less',
                dest: 'build/css/<%= pkg.originName %>-responsive.css'
            },
            compileRtl: {
                src: 'less/<%= pkg.originName %>-rtl.less',
                dest: 'build/css/<%= pkg.originName %>-rtl.css'
            },
            compileSchemes: {
                src: 'less/<%= pkg.originName %>-schemes.less',
                dest: 'build/css/<%= pkg.originName %>-schemes.css'
            },
            compileFont: {
                src: 'less/<%= pkg.originName %>-icons.less',
                dest: 'build/css/<%= pkg.originName %>-icons.css'
            }
        },

        postcss: {
            options: {
                processors: [
                    autoprefixer({ browsers: ['> 5%'] })
                ]
            },
            dist: { src: 'build/css/*.css' }
        },

        cssmin: {
            minCore: {
                src: 'build/css/<%= pkg.originName %>.css',
                dest: 'build/css/<%= pkg.originName %>.min.css'
            },
            minRtl: {
                src: 'build/css/<%= pkg.originName %>-rtl.css',
                dest: 'build/css/<%= pkg.originName %>-rtl.min.css'
            },
            minResponsive: {
                src: 'build/css/<%= pkg.originName %>-responsive.css',
                dest: 'build/css/<%= pkg.originName %>-responsive.min.css'
            },
            minSchemes: {
                src: 'build/css/<%= pkg.originName %>-schemes.css',
                dest: 'build/css/<%= pkg.originName %>-schemes.min.css'
            },
            minFont: {
                src: 'build/css/<%= pkg.originName %>-icons.css',
                dest: 'build/css/<%= pkg.originName %>-icons.min.css'
            }
        },

        copy: {
            build_font: {
                src: 'fonts/*',
                dest: 'build/',
                expand: true
            },            
            docs_css_core: {
                src: 'build/css/<%= pkg.originName %>.css',
                dest: 'docs/css/<%= pkg.originName %>.css'
            },
            docs_css_rtl: {
                src: 'build/css/<%= pkg.originName %>-rtl.css',
                dest: 'docs/css/<%= pkg.originName %>-rtl.css'
            },
            docs_css_responsive: {
                src: 'build/css/<%= pkg.originName %>-responsive.css',
                dest: 'docs/css/<%= pkg.originName %>-responsive.css'
            },
            docs_css_schemes: {
                src: 'build/css/<%= pkg.originName %>-schemes.css',
                dest: 'docs/css/<%= pkg.originName %>-schemes.css'
            },
            docs_css_font: {
                src: 'build/css/<%= pkg.originName %>-icons.css',
                dest: 'docs/css/<%= pkg.originName %>-icons.css'
            },
            docs_js: {
                src: 'build/js/<%= pkg.originName %>.js',
                dest: 'docs/js/<%= pkg.originName %>.js'
            }
        },

        replace: {
            dist: {
                options: {
                    patterns: [
                        {
                            match: 'adsense',
                            replacement: '<%= grunt.file.read(".replace/google-adsense-block.txt") %>'
                        },
                        {
                            match: 'hit',
                            replacement: '<%= grunt.file.read(".replace/hit-ua-counter.txt") %>'
                        }
                    ]
                },
                files: [
                    {
                        expand: true,
                        flatten: true,
                        src: ['docs/*.html'], dest: '.compiled_html/'
                    }
                ]
            }
        },

        watch: {
            scripts: {
                files: ['js/*.js', 'js/utils/*.js', 'js/widgets/*js'],
                tasks: ['concat', 'uglify', 'copy:docs_js']
            }
        }
    });

    grunt.registerTask('default', [
        'clean', 'concat', 'uglify', 'less', 'postcss', 'cssmin', 'copy', /*'replace', */'watch'
    ]);

};
