# Working

## Resume

The Script searches for emails with the tag 'spam' after this it gets the current list of amavis blocked domains to make sure it will not enter repeated domains.

## Requirements
* Have a specific email receiving account with the subject 'Spam'.

## Known issues
* When the receiving email is set up in Zimbra with the zimbraSpamIsSpamAccount parameter **(Causing right-click email to open Spam, and it sends an email to Zimbra's spam account)** I was unable to get sender information without having to download email via API.

## Comments
The script was created like many others where a need arose to try to solve / minimize a problem as much as possible. And it doesn't mean that one should blindly follow this because there are thousands of solutions that seek to solve this problem with much more mastery.
