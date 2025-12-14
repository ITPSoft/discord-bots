# Bot configuration

## Grossmann

Make sure Grossman role has higher position than all self-service and gaming roles, otherwise the self-service buttons won't work.

## Šimek

As Šimek can be quite annoying, the channel he can reply to needs to

- allow any role Šimek bot has to post there
- be in ALLOW_CHANNELS

both need to be set up. This allows quick shutdown per channel.
To make the monitoring channel tidy, the 403 by Šimek are treated as a warning, not error, not getting into discord handler.
