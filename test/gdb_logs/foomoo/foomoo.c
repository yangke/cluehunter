int main()
{
	int a=1, b=2;
	int *p = &a;
	int *q = &b;
	int *c = q;
	*q=foo(&a,&b);
	*p=moo(p,c);
	moo(p,c);
	return 1/a;
}
int foo(int *x,int *y)
{
	return *x%=(*x)+(*y); 
}
int moo(int *x,int *y)
{
	return *x-*y;
}

