import { Injectable } from '@nestjs/common';

import { PrismaService } from '../prisma.service';

@Injectable()
export class TripsService {
    constructor(
        private readonly prisma: PrismaService,
    ) {}

    async list(userId: number) {
        return this.prisma.trip.findMany({
            where: { userId },
            orderBy: { createdAt: 'desc' },
        });
    }

    async stats(userId: number) {
        const result = await this.prisma.trip.aggregate({
            where: { userId },
            _count: { id: true },
            _avg: { budget: true },
        });

        return {
            total: result._count.id,
            averageBudget: result._avg.budget || 0,
        };
    }

    async create(data: any) {
        return this.prisma.trip.create({
            data: {
                destination: String(data.destination || ''),
                days: Number(data.days),
                budget: Number(data.budget),
                people: Number(data.people),
                interests: String(data.interests || ''),
                style: String(data.style || 'balanced'),
                result: data.result,
                userId: Number(data.userId),
            },
        });
    }
}
