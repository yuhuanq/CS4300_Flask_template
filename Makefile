#
# Makefile
# yqiu, 2019-04-29 13:05
#

deploy:
	sudo docker build -t yuhuanq/sonotype:latest -f kubernetes/Dockerfile .
	sudo docker push yuhuanq/sonotype:latest



# vim:ft=make
#
