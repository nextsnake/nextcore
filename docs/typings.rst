.. currentmodule:: nextcore.typings

Typings
=======

Common
------
.. class:: Snowflake

    A Discord Snowflake ID. This is a :class:`typing.NewType` of a :class:`str` representation of a :class:`int`.

    Read the `documentation <https://discord.dev/reference#Snowflakes>`__

Application
-----------
.. autoclass:: Application
    :members:
.. autoclass:: InstallParams
    :members:

Team
----
.. autoclass:: Team
    :members:

.. autoclass:: TeamMember
    :members:

.. class:: TeamPermission

    A :class:`User`'s permission in a :class:`Team`.


    Possible values
        - ``"*"``: All permissions

.. class:: MembershipState

    A `MembershipState <https://discord.dev/topics/teams#data-models-membership-state-enum>`__ object.

    A users membership state in a :class:`Team`.

    Possible values
        - 1: Invited
        - 2: Accepted

Audit log
---------
.. autoclass:: AuditLog
    :members:

.. autoclass:: AuditLogEntry
    :members:

.. class:: AuditLogEvent

   A `audit log event <https://discord.dev/resources/audit-log#audit-log-entry-object-audit-log-events>`__.

   Possible values
        - 1 
            This represents a ``GUILD_UPDATE`` audit log change.
        - 10 
            This represents a ``CHANNEL_CREATE`` audit log change.
        - 11 
            This represents a ``CHANNEL_UPDATE`` audit log change.
        - 12 
            This represents a ``CHANNEL_DELETE`` audit log change.
        - 13 
            This represents a ``CHANNEL_OVERWRITE_CREATE`` audit log change.
        - 14 
            This represents a ``CHANNEL_OVERWRITE_UPDATE`` audit log change.
        - 15 
            This represents a ``CHANNEL_OVERWRITE_DELETE`` audit log change.
        - 20 
            This represents a ``MEMBER_KICK`` audit log change.
        - 21 
            This represents a ``MEMBER_PRUNE`` audit log change.
        - 22 
            This represents a ``MEMBER_BAN_ADD`` audit log change.
        - 23 
            This represents a ``MEMBER_BAN_REMOVE`` audit log change.
        - 24 
            This represents a ``MEMBER_UPDATE`` audit log change.
        - 25 
            This represents a ``MEMBER_ROLE_UPDATE`` audit log change.
        - 26 
            This represents a ``MEMBER_MOVE`` audit log change.
        - 27 
            This represents a ``MEMBER_DISCONNECT`` audit log change.
        - 28 
            This represents a ``BOT_ADD`` audit log change.
        - 30 
            This represents a ``ROLE_CREATE`` audit log change.
        - 31 
            This represents a ``ROLE_UPDATE`` audit log change.
        - 32 
            This represents a ``ROLE_DELETE`` audit log change.
        - 40 
            This represents a ``INVITE_CREATE`` audit log change.
        - 41 
            This represents a ``INVITE_UPDATE`` audit log change.
        - 42 
            This represents a ``INVITE_DELETE`` audit log change.
        - 50 
            This represents a ``WEBHOOK_CREATE`` audit log change.
        - 51 
            This represents a ``WEBHOOK_UPDATE`` audit log change.
        - 52 
            This represents a ``WEBHOOK_DELETE`` audit log change.
        - 60 
            This represents a ``EMOJI_CREATE`` audit log change.
        - 61 
            This represents a ``EMOJI_UPDATE`` audit log change.
        - 62 
            This represents a ``EMOJI_DELETE`` audit log change.
        - 72 
            This represents a ``MESSAGE_DELETE`` audit log change.
        - 73 
            This represents a ``MESSAGE_BULK_DELETE`` audit log change.
        - 74 
            This represents a ``MESSAGE_PIN`` audit log change.
        - 75 
            This represents a ``MESSAGE_UNPIN`` audit log change.
        - 80 
            This represents a ``INTEGRATION_CREATE`` audit log change.
        - 81 
            This represents a ``INTEGRATION_UPDATE`` audit log change.
        - 82 
            This represents a ``INTEGRATION_DELETE`` audit log change.
        - 83 
            This represents a ``STAGE_INSTANCE_CREATE`` audit log change.
        - 84 
            This represents a ``STAGE_INSTANCE_UPDATE`` audit log change.
        - 85 
            This represents a ``STAGE_INSTANCE_DELETE`` audit log change.
        - 90 
            This represents a ``STICKER_CREATE`` audit log change.
        - 91 
            This represents a ``STICKER_UPDATE`` audit log change.
        - 92 
            This represents a ``STICKER_DELETE`` audit log change.
        - 100 
            This represents a ``GUILD_SCHEDULED_EVENT_CREATE`` audit log change.
        - 101 
            This represents a ``GUILD_SCHEDULED_EVENT_UPDATE`` audit log change.
        - 102 
            This represents a ``GUILD_SCHEDULED_EVENT_DELETE`` audit log change.
        - 110 
            This represents a ``THREAD_CREATE`` audit log change.
        - 111 
            This represents a ``THREAD_UPDATE`` audit log change.
        - 112 
            This represents a ``THREAD_DELETE`` audit log change.
        - 121 
            This represents a ``APPLICATION_COMMAND_PERMISSION_UPDATE`` audit log change.

.. autoclass:: AuditLogChange
    :members:

.. class:: AuditLogChangeKey
    
    A `audit log change key <https://discord.dev/resources/audit-log#audit-log-change-object-audit-log-change-key>`__ literal.

    Possible values
        - ``afk_channel_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Afk channel changed
        - ``afk_timeout``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Afk timeout duration changed
        - ``allow``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            A permission on a text or voice channel was allowed for a role
        - ``application_id``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Application id of the added or removed webhook or bot
        - ``archived``
            Object changed: ``thread``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Thread is now archived/unarchived
        - ``asset``
            Object changed: ``sticker``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Empty str
        - ``auto_archive_duration``
            Object changed: ``thread``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Auto archive duration changed
        - ``available``
            Object changed: ``sticker``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Availability of sticker changed
        - ``avatar_hash``
            Object changed: ``user``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            User avatar changed
        - ``banner_hash``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Guild banner changed
        - ``bitrate``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Voice channel bitrate changed
        - ``channel_id``
            Object changed: ``invite or guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Channel for invite code or guild scheduled event changed
        - ``code``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Invite code changed
        - ``color``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Role color changed
        - ``command_id``
            Object changed: ``application command permission``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Permissions for a command were updated
        - ``communication_disabled_until``
            Object changed: ``member``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`ISO8601 timestamp`

            Member timeout state changed
        - ``deaf``
            Object changed: ``member``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            User server deafened/undeafened
        - ``default_auto_archive_duration``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Default auto archive duration for newly created threads changed
        - ``default_message_notifications``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Default message notification level changed
        - ``deny``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            A permission on a text or voice channel was denied for a role
        - ``description``
            Object changed: ``guild, sticker, or guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Description changed
        - ``discovery_splash_hash``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Discovery splash changed
        - ``enable_emoticons``
            Object changed: ``integration``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Integration emoticons enabled/disabled
        - ``entity_type``
            Object changed: ``guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Entity type of guild scheduled event was changed
        - ``expire_behavior``
            Object changed: ``integration``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Integration expiring subscriber behavior changed
        - ``expire_grace_period``
            Object changed: ``integration``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Integration expire grace period changed
        - ``explicit_content_filter``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Change in whose messages are scanned and deleted for explicit content in the server
        - ``format_type``
            Object changed: ``sticker``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int (format type)`

            Format type of sticker changed
        - ``guild_id``
            Object changed: ``sticker``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Guild sticker is in changed
        - ``hoist``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Role is now displayed/no longer displayed separate from online users
        - ``icon_hash``
            Object changed: ``guild or role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Icon changed
        - ``image_hash``
            Object changed: ``guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Guild scheduled event cover image changed
        - ``id``
            Object changed: ``any``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            The id of the changed entity - sometimes used in conjunction with other keys
        - ``invitable``
            Object changed: ``thread``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Private thread is now invitable/uninvitable
        - ``inviter_id``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Person who created invite code changed
        - ``location``
            Object changed: ``guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Change in channel id for guild scheduled event
        - ``locked``
            Object changed: ``thread``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Thread is now locked/unlocked
        - ``max_age``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            How long invite code lasts changed
        - ``max_uses``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Change to max number of times invite code can be used
        - ``mentionable``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Role is now mentionable/unmentionable
        - ``mfa_level``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Two-factor auth requirement changed
        - ``mute``
            Object changed: ``member``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            User server muted/unmuted
        - ``name``
            Object changed: ``any``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Name changed
        - ``nick``
            Object changed: ``member``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            User nickname changed
        - ``nsfw``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Channel nsfw restriction changed
        - ``owner_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Owner changed
        - ``permission_overwrites``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`array of channel overwrite objects`

            Permissions on a channel changed
        - ``permissions``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Permissions for a role changed
        - ``position``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Text or voice channel position changed
        - ``preferred_locale``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Preferred locale changed
        - ``privacy_level``
            Object changed: ``stage instance or guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int (privacy level)`

            Privacy level of the stage instance changed
        - ``prune_delete_days``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Change in number of days after which inactive and role-unassigned members are kicked
        - ``public_updates_channel_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Id of the public updates channel changed
        - ``rate_limit_per_user``
            Object changed: ``channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Amount of seconds a user has to wait before sending another message changed
        - ``region``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Region changed
        - ``rules_channel_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Id of the rules channel changed
        - ``splash_hash``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Invite splash page artwork changed
        - ``status``
            Object changed: ``guild scheduled event``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int (status)`

            Status of guild scheduled event was changed
        - ``system_channel_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Id of the system channel changed
        - ``tags``
            Object changed: ``sticker``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Related emoji of sticker changed
        - ``temporary``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Invite code is temporary/never expires
        - ``topic``
            Object changed: ``channel or stage instance``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Text channel topic or stage instance topic changed
        - ``type``
            Object changed: ``any``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int` | :class:`str`

            Type of entity created
        - ``unicode_emoji``
            Object changed: ``role``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Role unicode emoji changed
        - ``user_limit``
            Object changed: ``voice channel``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            New user limit in a voice channel
        - ``uses``
            Object changed: ``invite``

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Number of times invite code used changed
        - ``vanity_url_code``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`str`

            Guild invite vanity url changed
        - ``verification_level``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`int`

            Required verification level changed
        - ``widget_channel_id``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`Snowflake`

            Channel id of the server widget changed
        - ``widget_enabled``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`bool`

            Server widget enabled/disable
        - ``$add``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`array of partial role objects`

            New role added
        - ``$remove``
            Object changed: :class:`Guild`

            :attr:`AuditLogChange.new_value` and :attr:`AuditLogChange.old_value` will now be of type: :class:`array of partial role objects`

            Role removed

.. autoclass:: OptionalAuditEntryInfo
    :members:

Channel
-------
.. autoclass:: Channel
    :members:

.. class:: VideoQualityMode
    
    Video quality mode for a :class:`Voice channel <Channel>`.

    Possible values:
        - ``1`` Auto, Discord chooses the quality for optimal performance
        - ``2`` Full, 720p

.. class:: ChannelType
    
    A :data:`typing.Literal` representing the type of a :class:`Channel`.
    
    Possible values:
        - ``0``
          A text channel within a server

        - ``1``
          A direct message between users

        - ``2``
          A voice channel within a server

        - ``3``
          A direct message between multiple users

        - ``4``
          An organizational category that contains up to 50 channels

        - ``5``
          A channel that users can follow and crosspost into their own server

        - ``10``
          A temporary sub-channel within a GUILD_NEWS channel

        - ``11``
          A temporary sub-channel within a GUILD_TEXT channel

        - ``12``
          A temporary sub-channel within a GUILD_TEXT channel that is only viewable by those invited and those with the MANAGE_THREADS permission

        - ``13``
          A voice channel for hosting events with an audience

        - ``14``
          The channel in a hub containing the listed servers

        - ``15``
          (still in development) a channel that can only contain threads

.. autoclass:: Overwrite
    :members:

Thread
^^^^^^
.. class:: AutoArchiveDuration

    The time in minutes until a thread will be automatically archived after no activity.

    Possible values:
        - ``60`` 1 hour
        - ``1440`` 24 hours
        - ``4320`` 3 days
        - ``10080`` 7 days

.. autoclass:: ThreadMetadata
    :members:

.. autoclass:: ThreadMember
    :members:

Emoji
-----
.. autoclass:: Emoji
    :members:

Guild
-----
.. autoclass:: Guild
    :members:

.. class:: VerificationLevel
    
    A `Verification Level <https://discord.dev/resources/guild#guild-object-verification-level>`__ :data:`typing.Literal`.

    Possible values:
        - ``0``
          None
        - ``1``
          Must have a verified email.
        - ``2``
          Must be registered on Discord for longer than 5 minutes.
        - ``3``
          Must be a member of this guild for more than 10 minutes.
        - ``4``
          Must have a verified phone number.

.. class:: PremiumTier
    
    A `Premium Tier <https://discord.dev/resources/guild#guild-object-premium-tier>`__ :data:`typing.Literal`.

    Possible values:
        - ``0``
          None
        - ``1``
          Tier 1
        - ``2``
          Tier 2
        - ``3``
          Tier 3

.. class:: GuildFeature
    
    A `Guild Feature <https://discord.dev/resources/guild#guild-object-guild-features>`__ :data:`typing.Literal`.

    Possible values:
        - ``ANIMATED_BANNER``
          Guild has access to set an animated guild banner image
        - ``ANIMATED_ICON``
          Guild has access to set an animated guild icon
        - ``BANNER``
          Guild has access to set a guild banner image
        - ``COMMERCE``
          Guild has access to use commerce features (i.e. create store channels)
        - ``COMMUNITY``
          Guild can enable welcome screen, Membership Screening, stage channels and discovery, and receives community updates
        - ``DISCOVERABLE``
          Guild is able to be discovered in the directory
        - ``FEATURABLE``
          Guild is able to be featured in the directory
        - ``INVITE_SPLASH``
          Guild has access to set an invite splash background
        - ``MEMBER_VERIFICATION_GATE_ENABLED``
          Guild has enabled Membership Screening
        - ``MONETIZATION_ENABLED``
          Guild has enabled monetization
        - ``MORE_STICKERS``
          Guild has increased custom sticker slots
        - ``NEWS``
          Guild has access to create news channels
        - ``PARTNERED``
          Guild is partnered
        - ``PREVIEW_ENABLED``
          Guild can be previewed before joining via Membership Screening or the directory
        - ``PRIVATE_THREADS``
          Guild has access to create private threads
        - ``ROLE_ICONS``
          Guild is able to set role icons
        - ``SEVEN_DAY_THREAD_ARCHIVE``
          Guild has access to the seven day archive time for threads
        - ``THREE_DAY_THREAD_ARCHIVE``
          Guild has access to the three day archive time for threads
        - ``TICKETED_EVENTS_ENABLED``
          Guild has enabled ticketed events
        - ``VANITY_URL``
          Guild has access to set a vanity URL
        - ``VERIFIED``
          Guild is verified
        - ``VIP_REGIONS``
          Guild has access to set 384kbps bitrate in voice (previously VIP voice servers)
        - ``WELCOME_SCREEN_ENABLED``
          Guild has enabled the welcome screen

.. class:: DefaultNotitificationLevel

    A `Default Notification Level <https://discord.dev/resources/guild#guild-object-default-message-notification-level>`__ :data:`typing.Literal`.

    Possible values:
        - ``0``
          All messages
        - ``1``
          Only mentions

.. class:: GuildNSFWLevel

   A `Guild NSFW Level <https://discord.dev/resources/guild#guild-object-guild-nsfw-level>`__ :data:`typing.Literal`.

   Possible values:
        - ``0``
          Default
        - ``1``
          Explicit
        - ``2``
          Safe
        - ``3``
          Age restricted

.. class:: MFALevel

   A `MFA Level <https://discord.dev/resources/guild#guild-object-mfa-level>`__ :data:`typing.Literal`.

   Possible values:
        - ``0``
          Guild has no MFA/2FA requirement for moderation actions
        - ``1``
          Guild has a 2FA requirement for moderation actions
