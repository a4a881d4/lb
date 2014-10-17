f = fopen('rightAccP.txt','rt');
x = fscanf(f, '%f',[87,1024]);
mx = max(max(x))*8.;
x = x/mx*255;
imshow(x);
colormap(hot);


