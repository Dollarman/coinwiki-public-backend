var gulp         = require("gulp"),
    sass         = require("gulp-sass"),
    autoprefixer = require("gulp-autoprefixer"),
    hash         = require("gulp-hash"),
    del          = require("del"),
    concat       = require('gulp-concat')
    ;

// Compile SCSS files to CSS
gulp.task("scss", function () {

    //Delete our old css files
    del(["static/theme-flex/style-*.css"])

    gulp.src("compile/scss/style.scss")
        .pipe(sass({
            outputStyle : "compressed"
        }))
        .pipe(autoprefixer({
            browsers : ["last 20 versions"]
        }))
        .pipe(hash())
        .pipe(gulp.dest("static/theme-flex")) //output css files
        //Create a hash map
        .pipe(hash.manifest("hashmap_css.json"))
        //Put the map in the data directory
        .pipe(gulp.dest("data"))

})



// Watch asset folder for changes
gulp.task("watch", ["scss"], function () {
    gulp.watch("compile/scss/*", ["scss"])
})

// Set watch as default task
gulp.task("default", ["watch"])
