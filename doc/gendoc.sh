#!/bin/bash
# echo "Hello World!"
# echo $1
this_path=`pwd`
src_path=`cd ..;pwd`

while :
do
    echo -e "Project's location is ${src_path} \ndoc will generate in ${this_path}"
    if test -n "$1" && test "$1" = "-y"
    then
        aInput=y
        echo "Are You Sure (Y/N)y"
    else
        echo -e "Are You Sure (Y/N)\c"
        read aInput
    fi
    case $aInput in
        Y|y) sphinx-apidoc --ext-autodoc -f -o ${this_path} ${src_path}
             make clean
             make html
             break
            ;;
        N|n) echo "bye"
            break
            ;;
        *)
            ;;
    esac
done

# sphinx-apidoc --ext-autodoc -f -o ${this_path} ${src_path}
# make clean
# make html