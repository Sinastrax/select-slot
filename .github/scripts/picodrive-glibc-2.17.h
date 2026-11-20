/* PicoDrive sound calls log/pow. Bind them to the H700's GLIBC_2.17 ABI. */
__asm__(".symver log,log@GLIBC_2.17");
__asm__(".symver pow,pow@GLIBC_2.17");
