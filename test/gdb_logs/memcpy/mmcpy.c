#include<stdio.h>
#include<stdlib.h>
void cpy_it(char *dst,char *src,int len)
{
	memcpy(dst,src,len);
}
void main()
{
	
	char b[100]="12345600000000000000000000000000000000000000000000000000000000000";
	char buffer[100];
	char a[2]="1";
	cpy_it(buffer,b,100);
	cpy_it(a,buffer,1000);
}
