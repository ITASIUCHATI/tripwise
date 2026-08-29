import { Module } from '@nestjs/common';

import { AuthModule } from '../auth/auth.module';
import { TripsModule } from '../trips/trips.module';
import { RecommendationsController } from './recommendations.controller';
import { RecommendationsService } from './recommendations.service';

@Module({
    imports: [AuthModule, TripsModule],
    controllers: [RecommendationsController],
    providers: [RecommendationsService],
})
export class RecommendationsModule {}
