import { RankItem } from "@/components/LeaderBoardItem";
import { BarsArrowUpIcon,BarsArrowDownIcon } from '@heroicons/react/24/solid'
import Image from "next/image";
const LeaderBoard = () => {
    return ( 
        <div className=" p-6 h-full mx-auto bg-slate-100 text-gray-800">
            <div className="flex flex-col">
                <div className="rounded-lg shadow-lg h-full block bg-white">
                        <div className="p-8">
                            <h5 className="text-2xl font-bold">LeaderBoard</h5>
                        </div>
                         <div className="flex flex-row justify-between px-6 py-3 font-semibold text-md">
                            <div className="flex flex-row items-center justify-center space-x-2">
                                
                                <div>
                                <p>Rank</p>
                                </div>
                                <div className="mt-2  text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-inherit">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0l-3.75-3.75M17.25 21L21 17.25" />
                                </svg>

                            </div>
                            </div>
                             <div className="flex flex-row items-center justify-center space-x-2">
                                
                                <div>

                                <p>User</p>
                                </div>
                                <div className="mt-2 text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-inherit">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0l-3.75-3.75M17.25 21L21 17.25" />
                                </svg>

                            </div>
                            </div>
                              <div className="flex flex-row items-center justify-center space-x-2">
                                
                                <div>
                                <p>Score</p>
                                </div>
                                <div className="mt-2  text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-inherit">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0l-3.75-3.75M17.25 21L21 17.25" />
                                </svg>

                            </div>
                            </div>
                              <div className="flex flex-row items-center justify-center space-x-2">
                                
                                <div>
                                <p>Medal</p>
                                </div>
                            </div>
                        </div>
                        {/* leaderboard items */}
                        <RankItem></RankItem>



                </div>

            </div>

        </div>
     );
}
 
export default LeaderBoard;