# Host:
# Database: test
# Table: 'catalog'
#
CREATE TABLE `catalog` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `security_uid` INT UNSIGNED,
  `owner` varbinary(255) NOT NULL default '',
  `viewable_owner` varbinary(255) NOT NULL default '',
  `path` varchar(255) NOT NULL default '',
  `relative_url` varchar(255) NOT NULL default '',
  `parent_uid` BIGINT UNSIGNED default '0',
  `id` varchar(255) default '',
  `description` text,
  `title` varchar(255) default '',
  `meta_type` varchar(255) default '',
  `portal_type` varchar(255) default '',
  `opportunity_state` varchar(255) default '',
  `corporate_registration_code` varchar(255),
  `ean13_code` varchar(255),
  `validation_state` varchar(255) default '',
  `simulation_state` varchar(255) default '',
  `causality_state` varchar(255) default '',
  `invoice_state` varchar(255) default '',
  `payment_state` varchar(255) default '',
  `event_state` varchar(255) default '',
  `immobilisation_state` varchar(255) default '',
  `reference` varchar(255) binary default '',
  `grouping_reference` varchar(255) default '',
  `grouping_date` datetime,
  `source_reference` varchar(255) default '',
  `destination_reference` varchar(255) default '',
  `string_index` varchar(255),
  `int_index` INT,
  `float_index` real,
  `has_cell_content` bool,
  `creation_date` datetime,
  `modification_date` datetime,
  `indexation_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY  (`uid`),
  KEY `security_uid` (`security_uid`),
  KEY `owner` (`owner`),
  KEY `viewable_owner` (`viewable_owner`),
  KEY `Parent` (`parent_uid`),
  KEY `Path` (`path`),
  KEY `Title` (`title`),
  KEY `Reference` (`reference`),
  KEY `relative_url` (`relative_url`),
  KEY `Portal Type` (`portal_type`, `reference`),
  KEY `opportunity_state` (`opportunity_state`),
  KEY `validation_state_portal_type` (`validation_state`, `portal_type`),
  KEY `simulation_state_portal_type` (`simulation_state`, `portal_type`),
  KEY `causality_state_portal_type` (`causality_state`, `portal_type`),
  KEY `invoice_state` (`invoice_state`),
  KEY `payment_state` (`payment_state`),
  KEY `event_state` (`event_state`)
) ENGINE=InnoDB;
