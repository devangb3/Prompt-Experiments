"""
Database migration utility for moving data between MongoDB and Xano
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from .service import get_db_service
from .xano_service import get_xano_db_service
from .models import Conversation
from logging_config import get_logger

logger = get_logger("database.migration")


class DatabaseMigrationUtility:
    """Utility for migrating conversations between database providers"""
    
    def __init__(self):
        self.mongo_service = get_db_service()
        self.xano_service = get_xano_db_service()
        logger.info("Database migration utility initialized")
    
    async def migrate_all_conversations(self, batch_size: int = 100, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate all conversations from MongoDB to Xano
        
        Args:
            batch_size: Number of conversations to process in each batch
            dry_run: If True, only simulate the migration without actually saving
        
        Returns:
            Dictionary with migration statistics
        """
        logger.info(f"Starting migration {'(DRY RUN)' if dry_run else ''}")
        logger.info("=" * 50)
        
        stats = {
            "total_processed": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "errors": [],
            "start_time": datetime.utcnow(),
            "end_time": None
        }
        
        try:
            # Get all conversations from MongoDB
            logger.info("Fetching conversations from MongoDB...")
            all_conversations = await self.mongo_service.get_all_conversations(limit=10000)  # Adjust as needed
            total_conversations = len(all_conversations)
            
            logger.info(f"Found {total_conversations} conversations to migrate")
            
            if total_conversations == 0:
                logger.info("No conversations found in MongoDB")
                return stats
            
            # Process in batches
            for i in range(0, total_conversations, batch_size):
                batch = all_conversations[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_conversations + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} conversations)")
                
                for conversation in batch:
                    stats["total_processed"] += 1
                    
                    try:
                        if not dry_run:
                            # Check if conversation already exists in Xano
                            existing = await self.xano_service.get_conversation(conversation.conversation_id)
                            if existing:
                                logger.info(f"Skipping {conversation.conversation_id} (already exists in Xano)")
                                continue
                            
                            # Convert and save to Xano
                            await self._migrate_single_conversation(conversation)
                        
                        stats["successful_migrations"] += 1
                        logger.info(f"✓ Migrated {conversation.conversation_id}")
                        
                    except Exception as e:
                        stats["failed_migrations"] += 1
                        error_msg = f"Failed to migrate {conversation.conversation_id}: {str(e)}"
                        stats["errors"].append(error_msg)
                        logger.error(f"✗ {error_msg}")
                
                # Small delay between batches to avoid overwhelming the API
                if not dry_run and batch_num < total_batches:
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Migration failed with error: {e}")
            stats["errors"].append(f"Global error: {str(e)}")
        
        finally:
            stats["end_time"] = datetime.utcnow()
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            
            logger.info("=" * 50)
            logger.info("Migration Summary:")
            logger.info(f"Total processed: {stats['total_processed']}")
            logger.info(f"Successful: {stats['successful_migrations']}")
            logger.info(f"Failed: {stats['failed_migrations']}")
            logger.info(f"Duration: {duration:.2f} seconds")
            
            if stats["errors"]:
                logger.warning(f"Errors ({len(stats['errors'])}):")
                for error in stats["errors"][:10]:  # Show first 10 errors
                    logger.warning(f"  - {error}")
                if len(stats["errors"]) > 10:
                    logger.warning(f"  ... and {len(stats['errors']) - 10} more errors")
        
        return stats
    
    async def _migrate_single_conversation(self, mongo_conversation: Conversation):
        """Migrate a single conversation from MongoDB to Xano"""
        # Prepare messages for Xano
        from services.types import PromptMessage, AIResponse
        
        # Convert MongoDB models back to service types
        messages = [
            PromptMessage(role=msg.role, content=msg.content)
            for msg in mongo_conversation.messages
        ]
        
        responses = [
            AIResponse(
                provider=resp.provider,
                content=resp.content,
                model=resp.model,
                tokens_used=resp.tokens_used,
                error=resp.error
            )
            for resp in mongo_conversation.responses
        ]
        
        # Save to Xano
        await self.xano_service.save_conversation(
            messages=messages,
            responses=responses,
            conversation_id=mongo_conversation.conversation_id,
            metadata=mongo_conversation.metadata
        )
    
    async def verify_migration(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Verify that migrated conversations match the original data
        
        Args:
            sample_size: Number of conversations to verify
        
        Returns:
            Dictionary with verification statistics
        """
        logger.info("Verifying migration...")
        logger.info("=" * 30)
        
        verification_stats = {
            "checked": 0,
            "matches": 0,
            "mismatches": 0,
            "missing_in_xano": 0,
            "errors": []
        }
        
        try:
            # Get a sample of conversations from MongoDB
            mongo_conversations = await self.mongo_service.get_all_conversations(limit=sample_size)
            
            for conv in mongo_conversations:
                verification_stats["checked"] += 1
                
                try:
                    # Get the same conversation from Xano
                    xano_conv = await self.xano_service.get_conversation(conv.conversation_id)
                    
                    if not xano_conv:
                        verification_stats["missing_in_xano"] += 1
                        logger.error(f"✗ {conv.conversation_id} missing in Xano")
                        continue
                    
                    if (conv.conversation_id == xano_conv.conversation_id and
                        conv.system_prompt == xano_conv.system_prompt and
                        len(conv.messages) == len(xano_conv.messages) and
                        len(conv.responses) == len(xano_conv.responses)):
                        
                        verification_stats["matches"] += 1
                        logger.info(f"{conv.conversation_id} matches")
                    else:
                        verification_stats["mismatches"] += 1
                        logger.warning(f"{conv.conversation_id} mismatch")
                
                except Exception as e:
                    error_msg = f"Error verifying {conv.conversation_id}: {str(e)}"
                    verification_stats["errors"].append(error_msg)
                    logger.error(f"{error_msg}")
        
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            verification_stats["errors"].append(f"Global error: {str(e)}")
        
        logger.info("Verification Summary:")
        logger.info(f"Checked: {verification_stats['checked']}")
        logger.info(f"Matches: {verification_stats['matches']}")
        logger.info(f"Mismatches: {verification_stats['mismatches']}")
        logger.info(f"Missing in Xano: {verification_stats['missing_in_xano']}")
        
        return verification_stats


async def main():
    """Main function for running migrations"""
    import os
    
    # Check required environment variables
    if not os.getenv('XANO_BASE_URL'):
        logger.error("Error: XANO_BASE_URL environment variable must be set")
        return
    
    if not os.getenv('XANO_API_TOKEN'):
        logger.warning("Warning: XANO_API_TOKEN not set - using public endpoints")
    
    # Create migration utility
    migration_utility = DatabaseMigrationUtility()
    
    # Run migration
    logger.info("Starting MongoDB to Xano migration...")
    stats = await migration_utility.migrate_all_conversations(batch_size=50, dry_run=False)
    
    # Run verification
    logger.info("Running verification...")
    verification_stats = await migration_utility.verify_migration(sample_size=5)
    
    logger.info("Migration completed!")


if __name__ == "__main__":
    asyncio.run(main()) 