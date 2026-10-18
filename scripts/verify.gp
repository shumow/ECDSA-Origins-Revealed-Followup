chk(b,n,p)={my(E=ellinit([-3,b],p),Q); for(i=1,3, Q=random(E); if(ellmul(E,Q,n)!=[0], return(0))); 1};
{
P=2^224-2^96+1;
for(k=1,#C, if(C[k][1]==1708 || C[k][1]==2181 || C[k][1]==777 || C[k][1]==7026,
  b1=C[k][2]; b2=C[k][3];
  n2=ellsea(ellinit([-3,b2],P),1); n1=ellsea(ellinit([-3,b1],P),1);
  print(C[k][1]," n1=",n1," n2=",n2);
  if(n2, print("  n2 kills random pts on b1-curve: ",chk(b1,n2,P), "  on b2-curve: ",chk(b2,n2,P)));
  if(n1, print("  n1 kills random pts on b1-curve: ",chk(b1,n1,P), "  on b2-curve: ",chk(b2,n1,P)));
  print("  ellcard b1: ", ellcard(ellinit([-3,b1],P)), "  ellcard b2: ", ellcard(ellinit([-3,b2],P)));
));
}
quit
