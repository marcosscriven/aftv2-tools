#include <linux/module.h>
#include <linux/kallsyms.h>

// selinux function prototypes
typedef void (*selnl_notify_setenforce_t) (int val);
typedef void (*selinux_status_update_setenforce_t) (int enforcing);
typedef ssize_t (*sel_write_enforce_t) (
    struct file *file, const char __user *buf, size_t count, loff_t *ppos);

static int __init seldis_init (void) {

    // get selinux internal pointers
    int *selinux_enforcing = NULL;
    selnl_notify_setenforce_t selnl_notify_setenforce =
        (selnl_notify_setenforce_t)
        kallsyms_lookup_name("selnl_notify_setenforce");
    selinux_status_update_setenforce_t selinux_status_update_setenforce =
        (selinux_status_update_setenforce_t)
        kallsyms_lookup_name("selinux_status_update_setenforce");
    sel_write_enforce_t sel_write_enforce =
        (sel_write_enforce_t)
        kallsyms_lookup_name("sel_write_enforce");

    /*
      Procedure for finding offset to selinux_enforcing (5.0.3.1):

      aarch64-linux-android-objdump -D -b binary -m aarch64 --adjust-vma=0xffffffc000080000 kernel
      sel_write_enforce @ ffffffc000277e04
      ffffffc000277ec4:   900068b7    adrp    x23, 0xffffffc000f8b000 # +0xd14000
      ffffffc000277ecc:   b948cee0    ldr w0, [x23,#2252] # +0x8cc
    */

    // compute selinux_enforcing address
    if (sel_write_enforce != NULL) {
        selinux_enforcing = (int *)
            (((unsigned long)sel_write_enforce & ~0xffful) + 0xd148ccul);
    }

    // print debug info
    printk(KERN_INFO "[%s] selnl_notify_setenforce = %p\n",
        __this_module.name, selnl_notify_setenforce);
    printk(KERN_INFO "[%s] selinux_status_update_setenforce = %p\n",
        __this_module.name, selinux_status_update_setenforce);
    printk(KERN_INFO "[%s] sel_write_enforce = %p\n",
        __this_module.name, sel_write_enforce);
    printk(KERN_INFO "[%s] selinux_enforcing = %p\n",
        __this_module.name, selinux_enforcing);

    // validate pointer values
    if ((selinux_enforcing == NULL) ||
        (selnl_notify_setenforce == NULL) ||
        (selinux_status_update_setenforce == NULL)) {

        printk(KERN_ERR "[%s] SELinux cannot be changed\n",
            __this_module.name);
        return -1;
    }

    // set selinux to permissive
    *selinux_enforcing = 0;
    selnl_notify_setenforce(0);
    selinux_status_update_setenforce(0);

    printk(KERN_INFO "[%s] SELinux set to permissive\n",
        __this_module.name);

    return 0;
}

static void __exit seldis_exit (void) {}

module_init(seldis_init);
module_exit(seldis_exit);

MODULE_AUTHOR("Eric Work");
MODULE_DESCRIPTION("Set SELinux enforcing to permissive");
MODULE_LICENSE("GPL");

// vim: ai et ts=4 sts=4 sw=4
