import { Module } from '@nestjs/common';

import { AiModule } from './ai/ai.module';
import { AuthModule } from './auth/auth.module';
import { PrismaService } from './prisma.service';
import { RecommendationsModule } from './recommendations/recommendations.module';
import { TripsModule } from './trips/trips.module';

@Module({
    imports: [
        AuthModule,
        TripsModule,
        RecommendationsModule,
        AiModule,
    ],
    providers: [
        PrismaService,
    ],
    exports: [
        PrismaService,
    ],
})
export class AppModule {}