"""
Migration utility for transferring data from MongoDB to Xano
"""

import asyncio
import os
from typing import List, Dict, Any
from datetime import datetime
from .service import get_db_service
from .xano_service import get_xano_db_service
from .models import Conversation
from .xano_models import XanoConversation


class DatabaseMigrationUtility:
    """Utility for migrating conversations from MongoDB to Xano"""
    
    def __init__(self):
        self.mongo_service = get_db_service()
        self.xano_service = get_xano_db_service()
        
    async def migrate_all_conversations(self, batch_size: int = 100, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate all conversations from MongoDB to Xano
        
        Args:
            batch_size: Number of conversations to process in each batch
            dry_run: If True, only simulate the migration without actually transferring data
        
        Returns:
            Dictionary with migration statistics
        """
        print(f"Starting migration {'(DRY RUN)' if dry_run else ''}")
        print("=" * 50)
        
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
            print("Fetching conversations from MongoDB...")
            all_conversations = await self.mongo_service.get_all_conversations(limit=10000)  # Adjust as needed
            total_conversations = len(all_conversations)
            
            print(f"Found {total_conversations} conversations to migrate")
            
            if total_conversations == 0:
                print("No conversations found in MongoDB")
                return stats
            
            # Process in batches
            for i in range(0, total_conversations, batch_size):
                batch = all_conversations[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_conversations + batch_size - 1) // batch_size
                
                print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} conversations)")
                
                for conversation in batch:
                    stats["total_processed"] += 1
                    
                    try:
                        if not dry_run:
                            # Check if conversation already exists in Xano
                            existing = await self.xano_service.get_conversation(conversation.conversation_id)
                            if existing:
                                print(f"  Skipping {conversation.conversation_id} (already exists in Xano)")
                                continue
                            
                            # Convert and save to Xano
                            await self._migrate_single_conversation(conversation)
                        
                        stats["successful_migrations"] += 1
                        print(f"  ✓ Migrated {conversation.conversation_id}")
                        
                    except Exception as e:
                        stats["failed_migrations"] += 1
                        error_msg = f"Failed to migrate {conversation.conversation_id}: {str(e)}"
                        stats["errors"].append(error_msg)
                        print(f"  ✗ {error_msg}")
                
                # Small delay between batches to avoid overwhelming the API
                if not dry_run and batch_num < total_batches:
                    await asyncio.sleep(1)
        
        except Exception as e:
            print(f"Migration failed with error: {e}")
            stats["errors"].append(f"Global error: {str(e)}")
        
        finally:
            stats["end_time"] = datetime.utcnow()
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            
            print("\n" + "=" * 50)
            print("Migration Summary:")
            print(f"Total processed: {stats['total_processed']}")
            print(f"Successful: {stats['successful_migrations']}")
            print(f"Failed: {stats['failed_migrations']}")
            print(f"Duration: {duration:.2f} seconds")
            
            if stats["errors"]:
                print(f"\nErrors ({len(stats['errors'])}):")
                for error in stats["errors"][:10]:  # Show first 10 errors
                    print(f"  - {error}")
                if len(stats["errors"]) > 10:
                    print(f"  ... and {len(stats['errors']) - 10} more errors")
        
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
        
        # Calculate response times (if available)
        response_times = {}
        for resp in mongo_conversation.responses:
            if resp.response_time_ms:
                response_times[resp.provider] = resp.response_time_ms / 1000
        
        # Save to Xano
        await self.xano_service.save_conversation(
            messages=messages,
            responses=responses,
            conversation_id=mongo_conversation.conversation_id,
            metadata=mongo_conversation.metadata,
            response_times=response_times if response_times else None
        )
    
    async def verify_migration(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Verify migration by comparing a sample of conversations between MongoDB and Xano
        
        Args:
            sample_size: Number of conversations to verify
        
        Returns:
            Dictionary with verification results
        """
        print("Verifying migration...")
        print("=" * 30)
        
        verification_stats = {
            "checked": 0,
            "matches": 0,
            "mismatches": 0,
            "missing_in_xano": 0,
            "errors": []
        }
        
        try:
            # Get sample conversations from MongoDB
            mongo_conversations = await self.mongo_service.get_all_conversations(limit=sample_size)
            
            for conv in mongo_conversations:
                verification_stats["checked"] += 1
                
                try:
                    # Get corresponding conversation from Xano
                    xano_conv = await self.xano_service.get_conversation(conv.conversation_id)
                    
                    if not xano_conv:
                        verification_stats["missing_in_xano"] += 1
                        print(f"  ✗ {conv.conversation_id} missing in Xano")
                        continue
                    
                    # Compare basic properties
                    if (conv.conversation_id == xano_conv.conversation_id and
                        len(conv.messages) == len(xano_conv.messages) and
                        len(conv.responses) == len(xano_conv.responses)):
                        verification_stats["matches"] += 1
                        print(f"  ✓ {conv.conversation_id} matches")
                    else:
                        verification_stats["mismatches"] += 1
                        print(f"  ✗ {conv.conversation_id} mismatch")
                
                except Exception as e:
                    error_msg = f"Error verifying {conv.conversation_id}: {str(e)}"
                    verification_stats["errors"].append(error_msg)
                    print(f"  ✗ {error_msg}")
        
        except Exception as e:
            print(f"Verification failed: {e}")
            verification_stats["errors"].append(f"Global verification error: {str(e)}")
        
        print("\nVerification Summary:")
        print(f"Checked: {verification_stats['checked']}")
        print(f"Matches: {verification_stats['matches']}")
        print(f"Mismatches: {verification_stats['mismatches']}")
        print(f"Missing in Xano: {verification_stats['missing_in_xano']}")
        
        return verification_stats


async def main():
    """Main function for running migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate conversations from MongoDB to Xano")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without transferring data")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of conversations per batch")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing migration")
    parser.add_argument("--verify-sample-size", type=int, default=10, help="Number of conversations to verify")
    
    args = parser.parse_args()
    
    if not os.getenv('XANO_BASE_URL'):
        print("Error: XANO_BASE_URL environment variable must be set")
        return
    
    if not os.getenv('XANO_API_TOKEN'):
        print("Warning: XANO_API_TOKEN not set - using public endpoints")
    
    migration_utility = DatabaseMigrationUtility()
    
    try:
        if args.verify_only:
            await migration_utility.verify_migration(sample_size=args.verify_sample_size)
        else:
            # Run migration
            stats = await migration_utility.migrate_all_conversations(
                batch_size=args.batch_size,
                dry_run=args.dry_run
            )
            
            # If migration was successful and not a dry run, verify a sample
            if not args.dry_run and stats["successful_migrations"] > 0:
                print("\nRunning verification...")
                await migration_utility.verify_migration(sample_size=min(10, stats["successful_migrations"]))
    
    finally:
        # Close connections
        from .connection import close_database
        await close_database()


if __name__ == "__main__":
    asyncio.run(main()) 