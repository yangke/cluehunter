	.file	"mmcpy.c"
	.text
.Ltext0:
	.globl	cpy_it
	.type	cpy_it, @function
cpy_it:
.LFB2:
	.file 1 "mmcpy.c"
	.loc 1 4 0
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	subl	$24, %esp
	.loc 1 5 0
	movl	16(%ebp), %eax
	movl	%eax, 8(%esp)
	movl	12(%ebp), %eax
	movl	%eax, 4(%esp)
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	memcpy
	.loc 1 6 0
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE2:
	.size	cpy_it, .-cpy_it
	.section	.rodata
	.align 4
.LC0:
	.string	"12345600000000000000000000000000000000000000000000000000000000000"
	.zero	34
	.text
	.globl	main
	.type	main, @function
main:
.LFB3:
	.loc 1 8 0
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	pushl	%edi
	pushl	%esi
	andl	$-16, %esp
	subl	$224, %esp
	.cfi_offset 7, -12
	.cfi_offset 6, -16
	.loc 1 8 0
	movl	%gs:20, %eax
	movl	%eax, 220(%esp)
	xorl	%eax, %eax
	.loc 1 10 0
	leal	20(%esp), %edx
	movl	$.LC0, %eax
	movl	$16, %ecx
	movl	%edx, %edi
	movl	%eax, %esi
	rep movsl
	movl	%esi, %eax
	movl	%edi, %edx
	movzwl	(%eax), %ecx
	movw	%cx, (%edx)
	addl	$2, %edx
	addl	$2, %eax
	leal	86(%esp), %edx
	movl	$0, %eax
	movw	%ax, (%edx)
	addl	$2, %edx
	movl	$8, %ecx
	movl	%edx, %edi
	rep stosl
	.loc 1 12 0
	movw	$49, 18(%esp)
	.loc 1 13 0
	movl	$100, 8(%esp)
	leal	20(%esp), %eax
	movl	%eax, 4(%esp)
	leal	120(%esp), %eax
	movl	%eax, (%esp)
	call	cpy_it
	.loc 1 14 0
	movl	$1000, 8(%esp)
	leal	120(%esp), %eax
	movl	%eax, 4(%esp)
	leal	18(%esp), %eax
	movl	%eax, (%esp)
	call	cpy_it
	.loc 1 15 0
	movl	220(%esp), %eax
	xorl	%gs:20, %eax
	je	.L3
	call	__stack_chk_fail
.L3:
	leal	-8(%ebp), %esp
	popl	%esi
	.cfi_restore 6
	popl	%edi
	.cfi_restore 7
	popl	%ebp
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE3:
	.size	main, .-main
.Letext0:
	.file 2 "<built-in>"
	.section	.debug_info,"",@progbits
.Ldebug_info0:
	.long	0x139
	.value	0x4
	.long	.Ldebug_abbrev0
	.byte	0x4
	.uleb128 0x1
	.long	.LASF12
	.byte	0x1
	.long	.LASF13
	.long	.LASF14
	.long	.Ltext0
	.long	.Letext0-.Ltext0
	.long	.Ldebug_line0
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.long	.LASF0
	.uleb128 0x2
	.byte	0x1
	.byte	0x8
	.long	.LASF1
	.uleb128 0x2
	.byte	0x2
	.byte	0x7
	.long	.LASF2
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.long	.LASF3
	.uleb128 0x2
	.byte	0x1
	.byte	0x6
	.long	.LASF4
	.uleb128 0x2
	.byte	0x2
	.byte	0x5
	.long	.LASF5
	.uleb128 0x3
	.byte	0x4
	.byte	0x5
	.string	"int"
	.uleb128 0x2
	.byte	0x8
	.byte	0x5
	.long	.LASF6
	.uleb128 0x2
	.byte	0x8
	.byte	0x7
	.long	.LASF7
	.uleb128 0x2
	.byte	0x4
	.byte	0x5
	.long	.LASF8
	.uleb128 0x2
	.byte	0x4
	.byte	0x7
	.long	.LASF9
	.uleb128 0x4
	.byte	0x4
	.uleb128 0x5
	.byte	0x4
	.long	0x7a
	.uleb128 0x2
	.byte	0x1
	.byte	0x6
	.long	.LASF10
	.uleb128 0x5
	.byte	0x4
	.long	0x87
	.uleb128 0x6
	.uleb128 0x7
	.long	.LASF15
	.byte	0x1
	.byte	0x3
	.long	.LFB2
	.long	.LFE2-.LFB2
	.uleb128 0x1
	.byte	0x9c
	.long	0xe3
	.uleb128 0x8
	.string	"dst"
	.byte	0x1
	.byte	0x3
	.long	0x74
	.uleb128 0x2
	.byte	0x91
	.sleb128 0
	.uleb128 0x8
	.string	"src"
	.byte	0x1
	.byte	0x3
	.long	0x74
	.uleb128 0x2
	.byte	0x91
	.sleb128 4
	.uleb128 0x8
	.string	"len"
	.byte	0x1
	.byte	0x3
	.long	0x4f
	.uleb128 0x2
	.byte	0x91
	.sleb128 8
	.uleb128 0x9
	.long	.LASF16
	.byte	0x2
	.byte	0
	.long	0x72
	.uleb128 0xa
	.long	0x72
	.uleb128 0xa
	.long	0x81
	.uleb128 0xa
	.long	0x25
	.byte	0
	.byte	0
	.uleb128 0xb
	.long	.LASF17
	.byte	0x1
	.byte	0x7
	.long	.LFB3
	.long	.LFE3-.LFB3
	.uleb128 0x1
	.byte	0x9c
	.long	0x120
	.uleb128 0xc
	.string	"b"
	.byte	0x1
	.byte	0xa
	.long	0x120
	.uleb128 0x2
	.byte	0x74
	.sleb128 20
	.uleb128 0xd
	.long	.LASF11
	.byte	0x1
	.byte	0xb
	.long	0x120
	.uleb128 0x3
	.byte	0x74
	.sleb128 120
	.uleb128 0xc
	.string	"a"
	.byte	0x1
	.byte	0xc
	.long	0x130
	.uleb128 0x2
	.byte	0x74
	.sleb128 18
	.byte	0
	.uleb128 0xe
	.long	0x7a
	.long	0x130
	.uleb128 0xf
	.long	0x6b
	.byte	0x63
	.byte	0
	.uleb128 0x10
	.long	0x7a
	.uleb128 0xf
	.long	0x6b
	.byte	0x1
	.byte	0
	.byte	0
	.section	.debug_abbrev,"",@progbits
.Ldebug_abbrev0:
	.uleb128 0x1
	.uleb128 0x11
	.byte	0x1
	.uleb128 0x25
	.uleb128 0xe
	.uleb128 0x13
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x1b
	.uleb128 0xe
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x10
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x2
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0xe
	.byte	0
	.byte	0
	.uleb128 0x3
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0x8
	.byte	0
	.byte	0
	.uleb128 0x4
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x5
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x6
	.uleb128 0x26
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x7
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2116
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x8
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x9
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3c
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0xa
	.uleb128 0x5
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xb
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x6
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x2116
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xc
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0xd
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0xe
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xf
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x10
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_aranges,"",@progbits
	.long	0x1c
	.value	0x2
	.long	.Ldebug_info0
	.byte	0x4
	.byte	0
	.value	0
	.value	0
	.long	.Ltext0
	.long	.Letext0-.Ltext0
	.long	0
	.long	0
	.section	.debug_line,"",@progbits
.Ldebug_line0:
	.section	.debug_str,"MS",@progbits,1
.LASF6:
	.string	"long long int"
.LASF12:
	.string	"GNU C 4.8.2 -fpreprocessed -mtune=generic -march=i686 -g -fstack-protector"
.LASF0:
	.string	"unsigned int"
.LASF13:
	.string	"mmcpy.c"
.LASF17:
	.string	"main"
.LASF3:
	.string	"long unsigned int"
.LASF7:
	.string	"long long unsigned int"
.LASF1:
	.string	"unsigned char"
.LASF10:
	.string	"char"
.LASF8:
	.string	"long int"
.LASF16:
	.string	"memcpy"
.LASF14:
	.string	"/home/yangke/workspace/cluehunter/test/gdb_logs/memcpy"
.LASF2:
	.string	"short unsigned int"
.LASF4:
	.string	"signed char"
.LASF15:
	.string	"cpy_it"
.LASF5:
	.string	"short int"
.LASF11:
	.string	"buffer"
.LASF9:
	.string	"sizetype"
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
