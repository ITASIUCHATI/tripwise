import { Module } from '@nestjs/common';

import { AuthModule } from '../auth/auth.module';
import { PrismaService } from '../prisma.service';
import { TripsService } from '../trips/trips.service';
import { RecommendationsController } from './recommendations.controller';
import { RecommendationsService } from './recommendations.service';

@Module({
    imports: [AuthModule],
    controllers: [RecommendationsController],
    providers: [
        RecommendationsService,
        TripsService,
        PrismaService,
    ],
})
export class RecommendationsModule {}
