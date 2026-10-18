\\ exact orders for all candidates without 2-torsion; verified by scalar multiplication
chk(E,n)={my(Q); for(i=1,2, Q=random(E); if(ellmul(E,Q,n)!=[0], return(0))); 1};
{
for(k=1,#C,
  i=C[k][1]; b1=C[k][2];
  if(#polrootsmod(x^3-3*x+b1,P)>0, write(NAME".orders2", i," even"); next);
  E1=ellinit([-3,b1],P); n=ellcard(E1); m=2*P+2-n;
  if(chk(E1,n), write(NAME".orders2", i," ",n," ",m," ok"),
     if(chk(E1,m), write(NAME".orders2", i," ",m," ",n," signfix"), write(NAME".orders2", i," FAIL"))));
write(NAME".orders2","DONE");
}
quit
