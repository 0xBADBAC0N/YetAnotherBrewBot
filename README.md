# YetAnotherBrewBot

## get sd card
>> sudo fdisk -l

## unmount
>> sudo umount /dev/sdc1
>>  sudo umount /dev/sdc2

## backup current image
>> sudo dd if=/dev/sdc of=retropi_sd_card_copy.img

### to revert the backup do
>> sudo dd if=retropi_sd_card_copy.img of=/dev/sdc

